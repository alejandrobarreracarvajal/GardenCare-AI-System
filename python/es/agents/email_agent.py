from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import re 

# Instanciamos OllamaLLM
ollama_llm = OllamaLLM(model="deepseek-r1:32b", base_url="http://TU_IP_O_SERVIDOR:PUERTO")

# Prompt template para la redacción del email
# ⚠️ El usuario debe ingresar el correo del destinatario en tiempo de ejecución ⚠️
email_template_prompt = PromptTemplate(
    template=(
        "Eres un experto en botánica y cuidado de plantas, especialmente de Monstera adansonii. "
        "Basándote en el siguiente análisis de humedad del suelo para una planta de Monstera adansonii, "
        "redacta un email MUY CORTO Y CONCISO dirigido a {recipient_email}. "
        "El email debe:\n\n"
        "1. **Comienza el email ABSOLUTAMENTE con: `Hola,` (sin comillas, EXÁCTAMENTE así)**\n"
        "2. **Resumir de forma MUY CONCISA la evolución de la humedad del suelo** durante las fechas analizadas (extraídas de la tabla Markdown). Menciona solo lo más relevante.\n"
        "3. **Analizar de forma DIRECTA Y CONCISA si los valores de humedad son adecuados para una Monstera adansonii.** NO des consejos de riego manual, SIMPLEMENTE INDICA SI LOS NIVELES SON ADECUADOS O NO.\n"
        "4. **Identificar y mencionar de forma MUY BREVE si se detectan valores de humedad atípicos** (si los hay, sé muy directo).\n"
        "5. **Adjuntar un gráfico (mencionar que se adjunta).** Sé breve, solo indica que se adjunta un gráfico de humedad.\n"
        "6. **Cerrar el email con la siguiente despedida EXACTA:** Saludos cordiales, GardenCare AI System\n\n"
        "**IMPORTANTE:**\n"
        "- Utiliza un tono profesional, conciso e informativo.\n"
        "- Utiliza **formato HTML para poner en negrita las partes importantes del texto.**\n"
        "- **NO INCLUYAS el Asunto del email en el cuerpo del email.**\n"
        "- Sé **MUY BREVE Y DIRECTO en todo el email.**\n\n"
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        "    <meta charset='UTF-8'>\n"
        "</head>\n"
        "<body>\n"
        "    <p><strong>Hola,</strong></p>\n"
        "    <p>Analizando los datos de humedad del suelo para su Monstera adansonii del [FECHA INICIO] al [FECHA FIN]:</p>\n"
        "    <ul>\n"
        "        <li>Humedad promedio: entre <strong>[RANGO HUMEDAD MIN-MAX]%</strong>. <strong>[FRASE SI LOS VALORES SON ADECUADOS]</strong></li>\n"
        "    </ul>\n"
        "    <p><strong>[FRASE DE SUGERENCIA BASADA EN EL ANÁLISIS].</strong></p>\n"
        "    <p>[FRASE VALORES ATÍPICOS, SI APLICA, SI NO, NO MENCIONAR NADA].</p>\n"
        "    <p>Adjunto un gráfico con la evolución detallada de la humedad del suelo.</p>\n"
        "    <p><strong>Saludos cordiales,</strong></p>\n"
        "    <p>GardenCare AI System</p>\n"
        "</body>\n"
        "</html>\n\n"
        "Datos de humedad del suelo (tabla Markdown):\n"
        "{markdown_table}\n\n"
        "**DEVUELVE SOLO EL CÓDIGO HTML COMPLETO DEL EMAIL**"
    ),
    input_variables=["markdown_table", "recipient_email"]
)

email_chain = LLMChain(llm=ollama_llm, prompt=email_template_prompt)

def analyze_humidity_and_draft_email():
    """
    Función principal para analizar los datos de humedad, redactar y enviar el email.
    """
    # El usuario debe ingresar las rutas de los archivos
    report_path_md = input("Ingrese la ruta del archivo Markdown de humedad: ").strip()
    image_path_png = input("Ingrese la ruta del gráfico de humedad (.png): ").strip()
    recipient_email = input("Ingrese el correo del destinatario: ").strip()
    sender_email = input("Ingrese su correo de Gmail remitente: ").strip()
    sender_password = getpass("Ingrese contraseña de aplicación): ")  # Entrada segura

    print(f"\n[DEBUG] Leyendo reporte Markdown desde: {report_path_md}")

    # --- Leer y procesar los datos de humedad ---
    try:
        df_humidity = pd.read_csv(report_path_md, sep='|', skiprows=[2], skipinitialspace=True, header=0)
        df_humidity.columns = df_humidity.columns.str.strip()  # Limpiar nombres de columnas
        df_humidity = df_humidity.dropna(axis=1, how='all')  # Eliminar columnas vacías si existen
        print("\n[DEBUG] DataFrame de humedad leído exitosamente.")
        print(df_humidity.to_markdown(index=False))  # Debug: Mostrar tabla
    except Exception as e:
        print(f"\n[ERROR] Error al leer el archivo Markdown: {e}")
        return

    # --- Generar el email con Langchain ---
    markdown_table_content = df_humidity.to_markdown(index=False)

    try:
        print("\n[DEBUG] Generando borrador de email...")
        email_draft = email_chain.run(markdown_table=markdown_table_content, recipient_email=recipient_email)
        print("\n[DEBUG] Borrador de email generado.")

        # --- Extraer el HTML del email ---
        match = re.search(r"<!DOCTYPE html>(.*?)</html>", email_draft, re.DOTALL | re.IGNORECASE)
        extracted_email_html = match.group(0) if match else email_draft.strip()

    except Exception as e:
        print(f"\n[ERROR] Error al generar el email con Langchain: {e}")
        return

    # --- Preparar el email ---
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Reporte humedad {datetime.now().strftime('%d/%m/%Y')}"
    msg.attach(MIMEText(extracted_email_html, 'html'))  # Agregar email en HTML

    # --- Adjuntar la imagen ---
    try:
        with open(image_path_png, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path_png))
            msg.attach(img)
        print(f"\n[DEBUG] Imagen adjuntada: {image_path_png}")

    except Exception as e:
        print(f"\n[ERROR] Error al adjuntar la imagen: {e}")
        return

    # --- Enviar el email ---
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print("\n✅ Email enviado exitosamente a:", recipient_email)

    except Exception as e:
        print(f"\n[ERROR] Error al enviar el email: {e}")

    finally:
        if 'server' in locals():
            server.quit()  # Cerrar conexión SMTP

if __name__ == "__main__":
    analyze_humidity_and_draft_email()