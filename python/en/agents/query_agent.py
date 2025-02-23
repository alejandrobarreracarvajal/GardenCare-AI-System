from langchain_ollama import OllamaLLM
from langchain_community.utilities import SQLDatabase
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# Language model configuration
ollama_llm = OllamaLLM(model="llama3.1", base_url="http://YOUR_IP_OR_SERVER:PORT")

# Database configuration
DB_USER = os.getenv("DB_USER", "user_here")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password_here")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "database_name")

# Connection URI construction
db_uri = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
database = SQLDatabase.from_uri(db_uri)

# Template for generating the SQL query
query_gen_template = PromptTemplate(
    template=(
        "You are an SQL expert. Given the following instruction, generate a valid SQL query for PostgreSQL.\n"
        "The SQL query must be **only the SQL code**, without explanations, comments, or code block delimiters (like `sql or `).\n"
        "Instruction: {instruction}\n"
        "SQL Query:"
    ),
    input_variables=["instruction"]
)
query_gen_chain = LLMChain(llm=ollama_llm, prompt=query_gen_template)

# Template for generating the report in Markdown format
report_template = PromptTemplate(
    template=(
        "You are a data analyst. Based on the following results obtained from the database, "
        "generate a detailed report in Markdown format. The report should include the date, minimum value, "
        "average value, and maximum value for each date, and present the values with exactly two decimal places. "
        "The results should be presented in a table with the following columns: 'date', 'min_value', 'avg_value', "
        "and 'max_value'.\n\n"
        "- Numeric values should be right-aligned.\n"
        "- Ensure that numeric values (minimum, average, maximum) have two decimal places.\n"
        "- Results should be in ascending order by date.\n\n"
        "Results:\n{results}\n"
        "Report:"
    ),
    input_variables=["results"]
)
report_chain = LLMChain(llm=ollama_llm, prompt=report_template)

def research_task():
    """Generates the SQL query using LangChain."""
    instruction = (
        "Generate a valid SQL query for PostgreSQL that selects, for each date of the last three days, the date, minimum value, "
        "average value, and maximum value of the 'value' column from the 'sensor_data' table. "
        "The query should group the results by date (excluding the time) and round the minimum, average, and maximum values to two decimal places. "
        "Also, the results should be ordered in ascending order by date. "
        "Only respond with the SQL query, without explanations, observations, conclusions, or comments."
    )
    return query_gen_chain.run(instruction=instruction)

def reporting_task(sql_query):
    """Executes the SQL query and generates the report."""
    print("\n[INFO] Executing SQL query:")
    print(sql_query)

    # Execute the query in the database
    results = database.run(sql_query)

    print("\n[INFO] Results obtained:")
    print(results)

    return report_chain.run(results=results)

def run_workflow():
    """
    Executes the complete workflow: generates the SQL query, executes it, and generates the report.
    If the query fails, it attempts to regenerate and retry up to a maximum of 5 times.
    """
    max_attempts = 5
    attempt = 0
    report = None

    while attempt < max_attempts:
        print(f"\n[INFO] Attempt {attempt+1} of {max_attempts} to generate and execute the SQL query.")
        sql_query = research_task()

        try:
            report = reporting_task(sql_query)
            print("\n[INFO] Report generated successfully.")
            break  # If the query executes successfully, exit the loop.
        except Exception as e:
            print(f"\n[ERROR] The query failed with error: {e}")
            attempt += 1

            if attempt < max_attempts:
                print("[INFO] Regenerating query and retrying...")
            else:
                print("[ERROR] Maximum number of attempts reached. Aborting process.")
                return

    # Save the report to a file if obtained
    if report:
        report_path = os.getenv("REPORT_PATH", "results_report.md")
        with open(report_path, "w") as f:
            f.write(report)
        print(f"\n[INFO] Report saved to {report_path}")

if __name__ == "__main__":
    run_workflow()