#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// --- USER CONFIGURATION ---
// Fill in the following values with your own data:
const char* ssid = "YOUR_SSID";          // Replace with your WiFi network name
const char* password = "YOUR_PASSWORD";  // Replace with your WiFi password
const char* serverName = "http://YOUR_SERVER_IP/insert.php";  // Replace with your server's IP and the path to your PHP script

// Moisture threshold to activate the pump (adjust this value according to your calibration)
const int moistureThreshold = 250;  // Adjust based on your sensor
// --- END USER CONFIGURATION ---

// Sensor and pump pins
const int sensorPin = A0;   // Pin where the moisture sensor is connected
const int pumpPin = 2;      // Control pin for the pump

WiFiClient client;

void setup() {
  Serial.begin(9600);
  pinMode(sensorPin, INPUT);
  pinMode(pumpPin, OUTPUT);
  
  // Turn the pump off initially (assuming LOW activates the relay, so HIGH deactivates it)
  digitalWrite(pumpPin, HIGH);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 1. Read the moisture sensor
  int sensorValue = analogRead(sensorPin);
  Serial.print("Sensor value: ");
  Serial.println(sensorValue);

  // 2. Send data to the server (PHP script)
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(client, serverName);  // Start the connection to the server
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    http.setTimeout(5000);  // 5-second timeout

    // Prepare the data to send via POST
    String httpRequestData = "value=" + String(sensorValue);
    int httpResponseCode = http.POST(httpRequestData);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("Server response: ");
      Serial.println(response);
    } else {
      Serial.print("Error sending data, code: ");
      Serial.println(httpResponseCode);
    }
    http.end();  // Close the connection
  } else {
    Serial.println("WiFi connection error.");
  }

  // 3. Control the pump based on the sensor value
  if (sensorValue > moistureThreshold) {
    Serial.println("Soil is dry, activating pump...");
    digitalWrite(pumpPin, LOW);   // Activate the pump (relay active on LOW)
    delay(5000);                  // Pump on for 5 seconds
    digitalWrite(pumpPin, HIGH);  // Turn off the pump
    Serial.println("Pump deactivated.");
  } else {
    Serial.println("Soil moisture is adequate, pump not activated.");
  }

  // 4. Wait 1 hour before the next reading and action
  // Note: To optimize power consumption, consider implementing a deep sleep mode.
  delay(3600000);  // 1 hour = 3,600,000 milliseconds
}