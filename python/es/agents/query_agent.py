from langchain_ollama import OllamaLLM
from langchain_community.utilities import SQLDatabase
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# Configuración del modelo de lenguaje
ollama_llm = OllamaLLM(model="llama3.1", base_url="http://TU_IP_O_SERVIDOR:PUERTO")

# Configuración de la base de datos
DB_USER = os.getenv("DB_USER", "usuario_aqui")
DB_PASSWORD = os.getenv("DB_PASSWORD", "contraseña_aqui")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "nombre_base_datos")

# Construcción de la URI de conexión
db_uri = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
database = SQLDatabase.from_uri(db_uri)

# Plantilla para generar la consulta SQL
query_gen_template = PromptTemplate(
    template=(
        "Eres un experto en SQL. Dada la siguiente instrucción, genera una consulta SQL válida para PostgreSQL.\n"
        "La consulta SQL debe ser **solo el código SQL**, sin explicaciones, comentarios, ni delimitadores de bloque de código (como `sql o `).\n"
        "Instrucción: {instruction}\n"
        "Consulta SQL:"
    ),
    input_variables=["instruction"]
)
query_gen_chain = LLMChain(llm=ollama_llm, prompt=query_gen_template)

# Plantilla para generar el reporte en formato Markdown
report_template = PromptTemplate(
    template=(
        "Eres un analista de datos. A partir de los siguientes resultados obtenidos de la base de datos, "
        "genera un reporte detallado en formato markdown. El reporte debe incluir la fecha, el valor mínimo, "
        "el valor promedio y el valor máximo para cada fecha, y debe presentar los valores con exactamente dos decimales. "
        "Los resultados deben ser presentados en una tabla con las siguientes columnas: 'fecha', 'valor_minimo', 'valor_promedio' "
        "y 'valor_maximo'.\n\n"
        "- Los valores numéricos deben estar alineados a la derecha.\n"
        "- Asegúrate de que los valores numéricos (mínimo, promedio, máximo) tengan dos decimales.\n"
        "- Los resultados deben estar en orden ascendente según la fecha.\n\n"
        "Resultados:\n{results}\n"
        "Reporte:"
    ),
    input_variables=["results"]
)
report_chain = LLMChain(llm=ollama_llm, prompt=report_template)

def research_task():
    """Genera la consulta SQL usando LangChain."""
    instruction = (
        "Genera una consulta SQL válida para PostgreSQL que seleccione, para cada fecha de los últimos tres días, la fecha, el valor mínimo, "
        "el valor promedio y el valor máximo de la columna 'valor' de la tabla 'datos_sensor'. "
        "La consulta debe agrupar los resultados por fecha (sin incluir la hora) y redondear los valores mínimo, promedio y máximo a dos decimales. "
        "Además, los resultados deben ordenarse en orden ascendente por fecha. "
        "Solo responde con la consulta SQL, sin explicaciones, observaciones, conclusiones ni comentarios."
    )
    return query_gen_chain.run(instruction=instruction)

def reporting_task(sql_query):
    """Ejecuta la consulta SQL y genera el reporte."""
    print("\n[INFO] Ejecutando consulta SQL:")
    print(sql_query)

    # Ejecutar la consulta en la base de datos
    results = database.run(sql_query)

    print("\n[INFO] Resultados obtenidos:")
    print(results)

    return report_chain.run(results=results)

def run_workflow():
    """
    Ejecuta el flujo de trabajo completo: genera la consulta SQL, la ejecuta y genera el reporte.
    Si la query falla, se intenta regenerarla y reintentarlo hasta un máximo de 5 veces.
    """
    max_attempts = 5
    attempt = 0
    report = None

    while attempt < max_attempts:
        print(f"\n[INFO] Intento {attempt+1} de {max_attempts} para generar y ejecutar la consulta SQL.")
        sql_query = research_task()

        try:
            report = reporting_task(sql_query)
            print("\n[INFO] Reporte generado con éxito.")
            break  # Si la consulta se ejecuta correctamente, salir del bucle.
        except Exception as e:
            print(f"\n[ERROR] La consulta falló con el error: {e}")
            attempt += 1

            if attempt < max_attempts:
                print("[INFO] Regenerando consulta y reintentando...")
            else:
                print("[ERROR] Se alcanzó el número máximo de intentos. Abortando el proceso.")
                return

    # Guardar el reporte en un archivo si se obtuvo
    if report:
        report_path = os.getenv("REPORT_PATH", "reporte_resultados.md")
        with open(report_path, "w") as f:
            f.write(report)
        print(f"\n[INFO] Reporte guardado en {report_path}")

if __name__ == "__main__":
    run_workflow()
