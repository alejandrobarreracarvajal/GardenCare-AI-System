import os
import subprocess

# El usuario debe ingresar el directorio de salida para los archivos generados (reemplaza con tu propia ruta)
OUTPUT_DIR = input("Ingrese el directorio de salida para los archivos generados (ejemplo: /ruta/a/tu/directorio): ").strip()

def run_query_agent():
    print("[INFO] Ejecutando Query_agent.py...")
    subprocess.run(["python3", "Query_agent.py"], check=True)

def run_plot_agent():
    print("[INFO] Ejecutando Plot_agent.py...")
    subprocess.run(["python3", "Plot_agent.py"], check=True)

def run_email_agent():
    print("[INFO] Ejecutando Email_agent.py...")
    subprocess.run(["python3", "Email_agent.py"], check=True)

def cleanup_files():
    # Asegúrate de que OUTPUT_DIR esté configurado correctamente por el usuario.
    files_to_delete = [
        os.path.join(OUTPUT_DIR, "humedad_estimado.md"),
        os.path.join(OUTPUT_DIR, "humedad_suelo.png")
    ]
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[INFO] Archivo eliminado: {file_path}")
        else:
            print(f"[INFO] Archivo no encontrado (ya eliminado): {file_path}")

def main():
    try:
        run_query_agent()   # Ejecuta la tarea de generación de consulta y reporte Markdown
        run_plot_agent()    # Ejecuta la tarea de generación del gráfico (PNG y actualización del Markdown)
        run_email_agent()   # Ejecuta la tarea de redacción y envío del email
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ocurrió un error durante la ejecución: {e}")
    finally:
        cleanup_files()     # Elimina los archivos generados al finalizar el proceso

if __name__ == "__main__":
    main()
