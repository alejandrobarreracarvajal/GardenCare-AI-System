# GardenCare AI System

Bienvenido a GardenCare AI System, un proyecto 100% de código abierto que combina IoT, bases de datos y un sistema multiagentes (MAS) de IA para automatizar el cuidado de plantas. Este repositorio contiene el código en inglés y español, organizado por componente e idioma.

### Estructura del Repositorio
- `/arduino/`: Código de configuración de Arduino para el ESP8266 y el sensor de humedad HW-080.
  - `/en/`: Versión en inglés (`config.ino`)
  - `/es/`: Versión en español (`config.ino`)
- `/python/`: Scripts en Python para el backend y los agentes de IA.
  - `/en/`: Versiones en inglés de `main.py` y scripts de agentes (`query_agent.py`, `plot_agent.py`, `email_agent.py`).
  - `/es/`: Versiones en español de los mismos scripts.
- `/docs/`: Documentación en ambos idiomas.
  - `/en/README.md`: Documentación en inglés
  - `/es/README.md`: Documentación en español

### Tecnologías Utilizadas
- **Hardware**: ESP8266, sensor de humedad HW-080
- **Base de datos**: PostgreSQL (PgAdmin4)
- **Backend**: Apache/PHP
- **IA**: LangChain, Ollama, Llama 3.1, Deepseek-r1:32b
- **Visualización**: Python (Matplotlib)

### Cómo Usar
1. **Configura el hardware**:
   - Conecta el sensor de humedad HW-080 al ESP8266.
   - Carga la configuración de Arduino (`config.ino`) desde la carpeta `/arduino/en/` o `/arduino/es/`, según tu idioma preferido.
2. **Configura el backend**:
   - Instala Apache/PHP y PostgreSQL (PgAdmin4) en tu servidor local.
   - Configura la base de datos para recibir datos del ESP8266.
3. **Ejecuta los scripts en Python**:
   - Instala las dependencias: `pip install langchain ollama matplotlib`.
   - Ejecuta `main.py` desde la carpeta `/python/en/` o `/python/es/` para invocar los agentes de IA.
4. **Interactúa con los agentes de IA**:
   - `query_agent.py`: Extrae datos históricos de humedad y los organiza en Markdown.
   - `plot_agent.py`: Genera visualizaciones usando Matplotlib.
   - `email_agent.py`: Analiza datos y envía informes automáticos a Gmail.

### Contribuciones
Por favor, revisa los issues o envía pull requests. Asegúrate de especificar la versión de idioma en la que estás trabajando.
