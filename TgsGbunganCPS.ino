#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>

#define TRIG_PIN     6
#define ECHO_PIN     7
#define WATER_PIN    4   
#define BUZZER_PIN   14   
#define RELAY_PIN    2    

const char* WIFI_SSID     = "WIFI KAMU";
const char* WIFI_PASSWORD = "PASSWORD KAMU";
const char* BACKEND_URL   = "http://192.x.x.x:5001/api/iot";

const float CONTAINER_HEIGHT  = 19.0; 
const unsigned long INTERVAL  = 1000; 

const char* NTP_SERVER = "pool.ntp.org";
const long  GMT_OFFSET = 25200;  
const int   DST_OFFSET = 0;

unsigned long lastSendMs = 0;

void setup() {
  Serial.begin(115200);
  
  pinMode(TRIG_PIN,   OUTPUT);
  pinMode(ECHO_PIN,   INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RELAY_PIN,  OUTPUT);
  pinMode(WATER_PIN,  INPUT);

  digitalWrite(RELAY_PIN,   HIGH); 
  digitalWrite(BUZZER_PIN, LOW);

  connectWiFi();
  configTime(GMT_OFFSET, DST_OFFSET, NTP_SERVER);

  struct tm t;
  Serial.print("Menunggu sinkronisasi waktu");
  while (!getLocalTime(&t)) { delay(300); Serial.print("."); }
  Serial.println("\nWaktu Sinkron!");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
    return;
  }

  unsigned long now = millis();
  if (now - lastSendMs < INTERVAL) return;
  lastSendMs = now;

  float distance = readUltrasonicAvg(5); 
  int waterRaw = analogRead(WATER_PIN);
  float waterLevel = CONTAINER_HEIGHT - distance;
  if (waterLevel < 0) waterLevel = 0;

  String currentStatus = "normal";

  if (distance <= 8.0) {
    currentStatus = "bahaya";
    digitalWrite(RELAY_PIN, HIGH); 
    analogWrite(BUZZER_PIN, 3);     
  } 
  
  else if (distance <= 12.0) {
    currentStatus = "warning";

    if (distance < 9.0) {
      digitalWrite(RELAY_PIN, HIGH);
    } else {
      digitalWrite(RELAY_PIN, LOW); 
    }

    analogWrite(BUZZER_PIN, 3); delay(100); 
    analogWrite(BUZZER_PIN, 0); delay(100);
  }
  
  else {
    currentStatus = "normal";
    digitalWrite(RELAY_PIN, LOW);   
    analogWrite(BUZZER_PIN, 0);     
  }

  String timestamp = getTimestamp();
  
  Serial.printf("[IOT] Jarak: %.1f cm | WaterRaw: %d | Stat: %s\n", 
                distance, waterRaw, currentStatus.c_str());

  sendToBackend(timestamp, waterLevel, distance, waterRaw, currentStatus);
}

float readUltrasonicAvg(int n) {
  float sum = 0; int valid = 0;
  for (int i = 0; i < n; i++) {
    digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    long dur = pulseIn(ECHO_PIN, HIGH, 30000); 
    if (dur > 0) { 
      float d = (dur * 0.0343f) / 2.0f;
      if (d > 2.0 && d < 400.0) { 
        sum += d; valid++; 
      }
    }
    delay(10);
  }
  return (valid == 0) ? 0 : (sum / valid);
}

String getTimestamp() {
  struct tm t;
  if (!getLocalTime(&t)) return "1970-01-01 00:00:00";
  char buf[20];
  strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &t);
  return String(buf);
}

bool sendToBackend(String t, float level, float dist, int raw, String stat) {
  HTTPClient http;
  http.begin(BACKEND_URL);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<256> doc;
  doc["timestamp"]   = t;
  doc["water_level"] = level;
  doc["distance"]    = dist;
  doc["water_raw"]   = raw;
  doc["status"]      = stat;

  String payload;
  serializeJson(doc, payload);

  int code = http.POST(payload);
  Serial.print("[HTTP] Code: "); Serial.println(code);

  if (code < 0) Serial.println("[HTTP] Error: " + http.errorToString(code));
  
  http.end();
  return (code == 201 || code == 200);
}

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println(" Connected!");
}