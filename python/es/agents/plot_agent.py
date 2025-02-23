import os
import time
import re
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def obtener_ruta_directorio_salida():
    ruta_salida = input("Introduce la ruta completa del directorio de salida (ej: /home/usuario/salida): ")
    return ruta_salida

# Instanciamos OllamaLLM
ollama_llm = OllamaLLM(model="llama3.1", base_url="http://TU_IP_O_SERVIDOR:PUERTO")

# Obtenemos la ruta del directorio de salida del usuario
output_dir = obtener_ruta_directorio_salida()
os.makedirs(output_dir, exist_ok=True)

# Archivos esperados
expected_files = [
    os.path.join(output_dir, "humedad_suelo.png"),
    os.path.join(output_dir, "humedad_estimado.md"),
]

# Plantilla de generación de visualización (se mantiene igual)
plot_template = """ 
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = {data_placeholder}

df = pd.DataFrame(data)
df['Fecha'] = pd.to_datetime(df['Fecha'])

df['Humedad_min'] = (1023 - df['valor_maximo']) / 1023 * 100  
df['Humedad_prom'] = (1023 - df['valor_promedio']) / 1023 * 100
df['Humedad_max'] = (1023 - df['valor_minimo']) / 1023 * 100  

output_dir = r'{output_dir_placeholder}'
os.makedirs(output_dir, exist_ok=True)

md_path = os.path.join(output_dir, 'humedad_estimado.md')
with open(md_path, 'w') as f:
    f.write(df.to_markdown(index=False))

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('#1E1E1E')
ax.set_facecolor('#1E1E1E')

ax.fill_between(df['Fecha'], df['Humedad_min'], df['Humedad_max'],
                color='#A5D6A7', alpha=0.5, label='Rango Min/Max')

ax.plot(df['Fecha'], df['Humedad_prom'], color='#4CAF50', linewidth=2, label='Humedad Promedio')

ax.set_xlabel("Fecha", fontsize=12, fontweight='bold', color='white')
ax.set_ylabel("Porcentaje de Humedad (%)", fontsize=12, fontweight='bold', color='white')
ax.set_title("Humedad del Suelo por Día", fontsize=16, fontweight='bold', color='white', pad=40)
ax.set_xticks(df['Fecha'])
ax.set_xticklabels(df['Fecha'].dt.strftime('%Y-%m-%d'), fontsize=11, rotation=45, color='white')
ax.tick_params(axis='y', colors='white')

legend = ax.legend(frameon=False, fontsize=11, loc='upper center', bbox_to_anchor=(0.5, 1.13), ncol=2)
for text in legend.get_texts():
    text.set_color("white")

ax.grid(axis='y', linestyle='--', alpha=0.3, color='white')
plt.tight_layout()

png_path = os.path.join(output_dir, 'humedad_suelo.png')
plt.savefig(png_path)
"""

# Prompt template
visualization_template = PromptTemplate(
    template=(
        "Eres un experto en visualización de datos en Python. Se te proporciona un reporte en formato markdown "
        "con una tabla de datos actualizada de humedad del suelo. Tu tarea es extraer los datos de la tabla y generar "
        "un script de Python completo que use la siguiente plantilla EXACTAMENTE como base para el gráfico:\n\n"
        "{plot_template}\n\n"
        "NOTA: No utilices los datos de ejemplo que aparecen en la plantilla. Extrae la tabla real del reporte markdown y reemplaza "
        "la variable {{data_placeholder}} con el diccionario de Python correspondiente. El diccionario debe tener las claves: "
        "'Fecha', 'valor_minimo', 'valor_promedio' y 'valor_maximo', y sus valores deben ser listas con los datos extraídos.\n\n"
        "Reporte Markdown:\n{report_markdown_content}\n\nCódigo Python:"
    ),
    input_variables=["plot_template", "report_markdown_content"]
)

visualization_chain = LLMChain(llm=ollama_llm, prompt=visualization_template)

def extract_code_block(text):
    match = re.search(r"`(?:python)?\n(.*?)\n`", text, re.DOTALL)
    return match.group(1) if match else text

def generate_graph(output_dir): # Se agrega el output_dir como parametro
    report_path = os.path.join(output_dir, "report_langchain_direct_db.md")
    print(f"[INFO] Leyendo reporte desde: {report_path}")

    try:
        with open(report_path, "r") as f:
            report_markdown_content = f.read()
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo markdown: {e}")
        return False

    print("[INFO] Generando código Python...")
    python_code = visualization_chain.run(plot_template=plot_template.replace("{output_dir_placeholder}", output_dir), report_markdown_content=report_markdown_content) # Se remplaza el {output_dir_placeholder}

    python_code_clean = extract_code_block(python_code)
    print("[INFO] Código generado. Ejecutándolo...")

    try:
        exec(python_code_clean)
        print(f"[INFO] Archivos generados en {output_dir}")
        return True
    except Exception as e:
        print(f"[ERROR] Error al ejecutar el código Python: {e}")
        return False

def files_exist(output_dir):
    """ Verifica si los archivos esperados existen en el directorio de salida """
    expected_files = [
        os.path.join(output_dir, "humedad_suelo.png"),
        os.path.join(output_dir, "humedad_estimado.md"),
    ]
    return all(os.path.exists(file) for file in expected_files)

def main():
    max_attempts = 4  # Número máximo de intentos
    attempt = 0

    while attempt < max_attempts:
        print(f"\n[INFO] Intento {attempt + 1} de {max_attempts}")
        
        if files_exist(output_dir): # Se agrega el output_dir
            print("[INFO] Los archivos ya existen. No es necesario regenerarlos.")
            break

        print("[INFO] Generando archivos...")
        success = generate_graph(output_dir) # Se agrega el output_dir
        
        if success and files_exist(output_dir): # Se agrega el output_dir
            print("[INFO] Archivos generados exitosamente.")
            break

        print("[WARNING] No se generaron los archivos esperados. Reintentando...")
        attempt += 1
        time.sleep(2)  # Esperar un poco antes de reintentar

    if not files_exist(output_dir): # Se agrega el output_dir
        print("[ERROR] No se pudieron generar los archivos después de varios intentos.")

if __name__ == "__main__":
    main()