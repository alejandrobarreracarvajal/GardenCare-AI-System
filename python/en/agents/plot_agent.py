import os
import time
import re
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def get_output_directory_path():
    output_path = input("Enter the full path of the output directory (e.g., /home/user/output): ")
    return output_path

# Instantiate OllamaLLM
ollama_llm = OllamaLLM(model="llama3.1", base_url="http://YOUR_IP_OR_SERVER:PORT")

# Get the user's output directory path
output_dir = get_output_directory_path()
os.makedirs(output_dir, exist_ok=True)

# Expected files
expected_files = [
    os.path.join(output_dir, "soil_humidity.png"),
    os.path.join(output_dir, "estimated_humidity.md"),
]

# Visualization generation template (remains the same)
plot_template = """ 
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = {data_placeholder}

df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])

df['Humidity_min'] = (1023 - df['valor_maximo']) / 1023 * 100  
df['Humidity_avg'] = (1023 - df['valor_promedio']) / 1023 * 100
df['Humidity_max'] = (1023 - df['valor_minimo']) / 1023 * 100  

output_dir = r'{output_dir_placeholder}'
os.makedirs(output_dir, exist_ok=True)

md_path = os.path.join(output_dir, 'estimated_humidity.md')
with open(md_path, 'w') as f:
    f.write(df.to_markdown(index=False))

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('#1E1E1E')
ax.set_facecolor('#1E1E1E')

ax.fill_between(df['Date'], df['Humidity_min'], df['Humidity_max'],
                color='#A5D6A7', alpha=0.5, label='Min/Max Range')

ax.plot(df['Date'], df['Humidity_avg'], color='#4CAF50', linewidth=2, label='Average Humidity')

ax.set_xlabel("Date", fontsize=12, fontweight='bold', color='white')
ax.set_ylabel("Humidity Percentage (%)", fontsize=12, fontweight='bold', color='white')
ax.set_title("Soil Humidity by Day", fontsize=16, fontweight='bold', color='white', pad=40)
ax.set_xticks(df['Date'])
ax.set_xticklabels(df['Date'].dt.strftime('%Y-%m-%d'), fontsize=11, rotation=45, color='white')
ax.tick_params(axis='y', colors='white')

legend = ax.legend(frameon=False, fontsize=11, loc='upper center', bbox_to_anchor=(0.5, 1.13), ncol=2)
for text in legend.get_texts():
    text.set_color("white")

ax.grid(axis='y', linestyle='--', alpha=0.3, color='white')
plt.tight_layout()

png_path = os.path.join(output_dir, 'soil_humidity.png')
plt.savefig(png_path)
"""

# Prompt template
visualization_template = PromptTemplate(
    template=(
        "You are an expert in data visualization in Python. You are provided with a report in markdown format "
        "with an updated soil humidity data table. Your task is to extract the data from the table and generate "
        "a complete Python script that uses the following template EXACTLY as a base for the graph:\n\n"
        "{plot_template}\n\n"
        "NOTE: Do not use the example data that appears in the template. Extract the actual table from the markdown report and replace "
        "the {{data_placeholder}} variable with the corresponding Python dictionary. The dictionary should have the keys: "
        "'Date', 'valor_minimo', 'valor_promedio', and 'valor_maximo', and their values should be lists with the extracted data.\n\n"
        "Markdown Report:\n{report_markdown_content}\n\nPython Code:"
    ),
    input_variables=["plot_template", "report_markdown_content"]
)

visualization_chain = LLMChain(llm=ollama_llm, prompt=visualization_template)

def extract_code_block(text):
    match = re.search(r"`(?:python)?\n(.*?)\n`", text, re.DOTALL)
    return match.group(1) if match else text

def generate_graph(output_dir): # output_dir is added as a parameter
    report_path = os.path.join(output_dir, "report_langchain_direct_db.md")
    print(f"[INFO] Reading report from: {report_path}")

    try:
        with open(report_path, "r") as f:
            report_markdown_content = f.read()
    except Exception as e:
        print(f"[ERROR] Could not read markdown file: {e}")
        return False

    print("[INFO] Generating Python code...")
    python_code = visualization_chain.run(plot_template=plot_template.replace("{output_dir_placeholder}", output_dir), report_markdown_content=report_markdown_content) # Replace {output_dir_placeholder}

    python_code_clean = extract_code_block(python_code)
    print("[INFO] Code generated. Executing...")

    try:
        exec(python_code_clean)
        print(f"[INFO] Files generated in {output_dir}")
        return True
    except Exception as e:
        print(f"[ERROR] Error executing Python code: {e}")
        return False

def files_exist(output_dir):
    """ Checks if the expected files exist in the output directory """
    expected_files = [
        os.path.join(output_dir, "soil_humidity.png"),
        os.path.join(output_dir, "estimated_humidity.md"),
    ]
    return all(os.path.exists(file) for file in expected_files)

def main():
    max_attempts = 4  # Maximum number of attempts
    attempt = 0

    while attempt < max_attempts:
        print(f"\n[INFO] Attempt {attempt + 1} of {max_attempts}")
        
        if files_exist(output_dir): # output_dir is added
            print("[INFO] Files already exist. No need to regenerate them.")
            break

        print("[INFO] Generating files...")
        success = generate_graph(output_dir) # output_dir is added
        
        if success and files_exist(output_dir): # output_dir is added
            print("[INFO] Files generated successfully.")
            break

        print("[WARNING] Expected files were not generated. Retrying...")
        attempt += 1
        time.sleep(2)  # Wait a bit before retrying

    if not files_exist(output_dir): # output_dir is added
        print("[ERROR] Could not generate files after multiple attempts.")

if __name__ == "__main__":
    main()