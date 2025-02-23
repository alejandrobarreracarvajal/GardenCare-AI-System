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

# Instantiate OllamaLLM
ollama_llm = OllamaLLM(model="deepseek-r1:32b", base_url="http://YOUR_IP_OR_SERVER:PORT")

# Prompt template for drafting the email
# The user must enter the recipient's email at runtime
email_template_prompt = PromptTemplate(
    template=(
        "You are an expert in botany and plant care, particularly for Monstera adansonii. "
        "Based on the following soil moisture analysis for a Monstera adansonii, "
        "write a VERY SHORT AND CONCISE email addressed to {recipient_email}. "
        "The email should:\n\n"
        "1. **Start ABSOLUTELY with: `Hello,` (without quotes, EXACTLY like this)**\n"
        "2. **Summarize in a VERY CONCISE manner the evolution of soil moisture** over the analyzed dates (extracted from the Markdown table). Mention only the most relevant points.\n"
        "3. **Directly and concisely analyze whether the moisture levels are suitable for a Monstera adansonii.** DO NOT give manual watering tips; JUST STATE WHETHER THE LEVELS ARE APPROPRIATE OR NOT.\n"
        "4. **Briefly identify and mention any abnormal moisture values** (if present, be very direct).\n"
        "5. **Attach a graph (mention that it is attached).** Be brief; just state that a soil moisture graph is attached.\n"
        "6. **End the email with the following EXACT closing:** Best regards, GardenCare AI System\n\n"
        "**IMPORTANT:**\n"
        "- Use a professional, concise, and informative tone.\n"
        "- Use **HTML formatting to bold key parts of the text.**\n"
        "- **DO NOT INCLUDE the email subject in the email body.**\n"
        "- Be **VERY BRIEF AND TO THE POINT throughout the email.**\n\n"
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        "    <meta charset='UTF-8'>\n"
        "</head>\n"
        "<body>\n"
        "    <p><strong>Hello,</strong></p>\n"
        "    <p>Analyzing the soil moisture data for your Monstera adansonii from [START DATE] to [END DATE]:</p>\n"
        "    <ul>\n"
        "        <li>Average moisture: between <strong>[MIN-MAX MOISTURE RANGE]%</strong>. <strong>[STATEMENT ON WHETHER LEVELS ARE ADEQUATE]</strong></li>\n"
        "    </ul>\n"
        "    <p><strong>[SUGGESTION BASED ON ANALYSIS].</strong></p>\n"
        "    <p>[STATEMENT ON ABNORMAL VALUES, IF APPLICABLE, OTHERWISE OMIT].</p>\n"
        "    <p>Attached is a graph with a detailed evolution of soil moisture.</p>\n"
        "    <p><strong>Best regards,</strong></p>\n"
        "    <p>GardenCare AI System</p>\n"
        "</body>\n"
        "</html>\n\n"
        "Soil moisture data (Markdown table):\n"
        "{markdown_table}\n\n"
        "**RETURN ONLY THE COMPLETE HTML CODE OF THE EMAIL**"
    ),
    input_variables=["markdown_table", "recipient_email"]
)

email_chain = LLMChain(llm=ollama_llm, prompt=email_template_prompt)

def analyze_humidity_and_draft_email():
    """
    Main function to analyze humidity data, draft, and send the email.
    """
    # The user must enter the file paths
    report_path_md = input("Enter the path to the humidity Markdown file: ").strip()
    image_path_png = input("Enter the path to the humidity graph (.png): ").strip()
    recipient_email = input("Enter the recipient's email: ").strip()
    sender_email = input("Enter your Gmail sender email: ").strip()
    sender_password = getpass("Enter your app password: ")  #Secure input

    print(f"\n[DEBUG] Reading Markdown report from: {report_path_md}")

    # --- Read and process humidity data ---
    try:
        df_humidity = pd.read_csv(report_path_md, sep='|', skiprows=[2], skipinitialspace=True, header=0)
        df_humidity.columns = df_humidity.columns.str.strip()  # Clean column names
        df_humidity = df_humidity.dropna(axis=1, how='all')  # Remove empty columns if any
        print("\n[DEBUG] Humidity DataFrame successfully loaded.")
        print(df_humidity.to_markdown(index=False))  # Debug: Display table
    except Exception as e:
        print(f"\n[ERROR] Error reading the Markdown file: {e}")
        return

    # --- Generate the email with Langchain ---
    markdown_table_content = df_humidity.to_markdown(index=False)

    try:
        print("\n[DEBUG] Generating email draft...")
        email_draft = email_chain.run(markdown_table=markdown_table_content, recipient_email=recipient_email)
        print("\n[DEBUG] Email draft generated.")

        # --- Extract the email HTML content ---
        match = re.search(r"<!DOCTYPE html>(.*?)</html>", email_draft, re.DOTALL | re.IGNORECASE)
        extracted_email_html = match.group(0) if match else email_draft.strip()

    except Exception as e:
        print(f"\n[ERROR] Error generating the email with Langchain: {e}")
        return

    # --- Prepare the email ---
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Humidity Report {datetime.now().strftime('%d/%m/%Y')}"
    msg.attach(MIMEText(extracted_email_html, 'html'))  # Attach email content as HTML

    # --- Attach the image ---
    try:
        with open(image_path_png, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path_png))
            msg.attach(img)
        print(f"\n[DEBUG] Image attached: {image_path_png}")

    except Exception as e:
        print(f"\n[ERROR] Error attaching the image: {e}")
        return

    # --- Send the email ---
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print("\n✅ Email successfully sent to:", recipient_email)

    except Exception as e:
        print(f"\n[ERROR] Error sending the email: {e}")

    finally:
        if 'server' in locals():
            server.quit()  # Close SMTP connection

if __name__ == "__main__":
    analyze_humidity_and_draft_email()
