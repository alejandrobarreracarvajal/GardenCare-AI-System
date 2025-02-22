# GardenCare AI System / Sistema GardenCare AI

Welcome to the GardenCare AI System, a 100% open-source project that combines IoT, databases, and a multi-agent AI system (MAS) to automate plant care. This repository contains the code in both English and Spanish, organized by component and language.

### Repository Structure
- `/arduino/`: Arduino configuration code for the ESP8266 and HW-080 humidity sensor.
  - `/en/`: English version (`config.ino`)
  - `/es/`: Spanish version (`config.ino`)
- `/python/`: Python scripts for the backend and AI agents.
  - `/en/`: English versions of `main.py` and agent scripts (`query_agent.py`, `plot_agent.py`, `email_agent.py`).
  - `/es/`: Spanish versions of the same scripts.
- `/docs/`: Documentation in both languages.
  - `/en/README.md`: English documentation
  - `/es/README.md`: Spanish documentation

### Technologies Used
- **Hardware**: ESP8266, HW-080 humidity sensor
- **Database**: PostgreSQL (PgAdmin4)
- **Backend**: Apache/PHP
- **AI**: LangChain, Ollama, Llama 3.1, Deepseek-r1:32b
- **Visualization**: Python (Matplotlib)

### How to Use
1. **Set up the hardware**:
   - Connect the HW-080 humidity sensor to the ESP8266.
   - Upload the Arduino configuration (`config.ino`) from the `/arduino/en/` or `/arduino/es/` folder, depending on your preferred language.
2. **Set up the backend**:
   - Install Apache/PHP and PostgreSQL (PgAdmin4) on your local server.
   - Configure the database to receive data from the ESP8266.
3. **Run the Python scripts**:
   - Install dependencies: `pip install langchain ollama matplotlib`.
   - Run `main.py` from the `/python/en/` or `/python/es/` folder to invoke the AI agents.
4. **Interact with the AI agents**:
   - `query_agent.py`: Extracts historical humidity data and organizes it in Markdown.
   - `plot_agent.py`: Generates visualizations using Matplotlib.
   - `email_agent.py`: Analyzes data and sends automated reports to Gmail.

### Contributions
Please check the issues or submit pull requests. Make sure to specify the language version you're working on.
