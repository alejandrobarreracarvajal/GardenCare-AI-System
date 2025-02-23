import os
import subprocess

# The user must enter the output directory for the generated files (replace with your own path)
OUTPUT_DIR = input("Enter the output directory for the generated files (e.g., /path/to/your/directory): ").strip()

def run_query_agent():
    print("[INFO] Running Query_agent.py...")
    subprocess.run(["python3", "Query_agent.py"], check=True)

def run_plot_agent():
    print("[INFO] Running Plot_agent.py...")
    subprocess.run(["python3", "Plot_agent.py"], check=True)

def run_email_agent():
    print("[INFO] Running Email_agent.py...")
    subprocess.run(["python3", "Email_agent.py"], check=True)

def cleanup_files():
    # Ensure that OUTPUT_DIR is correctly provided by the user.
    files_to_delete = [
        os.path.join(OUTPUT_DIR, "humedad_estimado.md"),
        os.path.join(OUTPUT_DIR, "humedad_suelo.png")
    ]
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[INFO] File removed: {file_path}")
        else:
            print(f"[INFO] File not found (already removed): {file_path}")

def main():
    try:
        run_query_agent()   # Executes the query generation and Markdown report process
        run_plot_agent()    # Executes the graph generation (PNG and Markdown update)
        run_email_agent()   # Executes the email drafting and sending process
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] An error occurred during execution: {e}")
    finally:
        cleanup_files()     # Removes the generated files at the end of the process

if __name__ == "__main__":
    main()