#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// --- CONFIGURACIÓN DEL USUARIO ---
// Completa los siguientes valores con tus propios datos:
const char* ssid = "TU_SSID";            // Reemplaza con el nombre de tu red WiFi
const char* password = "TU_PASSWORD";    // Reemplaza con la contraseña de tu red WiFi
const char* serverName = "http://TU_SERVER_IP/insert.php";  // Reemplaza con la IP de tu servidor y ruta del script PHP

// Umbral de humedad para activar la bomba (ajusta este valor según tu calibración)
const int moistureThreshold = 250;  // Ajusta según tu sensor
// --- FIN CONFIGURACIÓN DEL USUARIO ---

// Pines del sensor y la bomba
const int sensorPin = A0;   // Pin donde se conecta el sensor de humedad
const int pumpPin = 2;      // Pin de control para la bomba

WiFiClient client;

void setup() {
  Serial.begin(9600);
  pinMode(sensorPin, INPUT);
  pinMode(pumpPin, OUTPUT);
  
  // Apaga la bomba inicialmente (se asume que LOW activa el relé, por lo que HIGH lo apaga)
  digitalWrite(pumpPin, HIGH);

  // Conectar a WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado a WiFi");
  Serial.print("Dirección IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 1. Leer el sensor de humedad
  int valorSensor = analogRead(sensorPin);
  Serial.print("Valor del sensor: ");
  Serial.println(valorSensor);

  // 2. Enviar datos al servidor (script PHP)
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(client, serverName);  // Inicia la conexión al servidor
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    http.setTimeout(5000);  // Timeout de 5 segundos

    // Prepara los datos para enviar vía POST
    String httpRequestData = "valor=" + String(valorSensor);
    int httpResponseCode = http.POST(httpRequestData);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("Respuesta del servidor: ");
      Serial.println(response);
    } else {
      Serial.print("Error al enviar datos, código: ");
      Serial.println(httpResponseCode);
    }
    http.end();  // Cierra la conexión
  } else {
    Serial.println("Error de conexión WiFi.");
  }

  // 3. Control de la bomba según el valor del sensor
  if (valorSensor > moistureThreshold) {
    Serial.println("Suelo seco, activando bomba...");
    digitalWrite(pumpPin, LOW);   // Activa la bomba (relé activo en LOW)
    delay(5000);                  // Bomba activada por 5 segundos
    digitalWrite(pumpPin, HIGH);  // Apaga la bomba
    Serial.println("Bomba desactivada.");
  } else {
    Serial.println("Humedad adecuada, no se activa la bomba.");
  }

  // 4. Espera 1 hora antes de la siguiente lectura y acción
  // Nota: Para optimizar el consumo de energía, considera implementar un modo de bajo consumo (deep sleep).
  delay(3600000);  // 1 hora = 3,600,000 milisegundos
}