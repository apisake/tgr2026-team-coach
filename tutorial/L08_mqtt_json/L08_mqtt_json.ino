// L08 · MQTT + JSON: ส่งค่าเซ็นเซอร์พร้อม lot_id + ts, LWT, รับคำสั่งจาก broker
//
// topic (แก้ให้ตรงกับ Data Contract ของทีม):
//   tgr2026/<team>/<node_id>/telemetry   ESP32 → broker   ค่าเซ็นเซอร์ทุก PUBLISH_MS
//   tgr2026/<team>/<node_id>/status      ESP32 → broker   "online" / "offline" (retain, LWT)
//   tgr2026/<team>/<node_id>/cmd         broker → ESP32   {"led":true} {"beep":2} {"lot_id":"L-002"} {"interval_ms":2000}

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>

// ---- ตั้งค่า ----
const char *WIFI_SSID = "YOUR_SSID";
const char *WIFI_PASS = "YOUR_PASSWORD";
const char *MQTT_HOST = "192.168.1.10";  // IP ของ Pi ที่รัน Mosquitto
const int MQTT_PORT = 1883;
const char *MQTT_USER = nullptr;          // ใส่ถ้า broker ตั้งรหัสผ่าน
const char *MQTT_PASS = nullptr;
const char *TEAM = "canet";
const char *NTP_SERVER = "pool.ntp.org";  // หรือ IP ของ Pi
const char *TZ_THAILAND = "<+07>-7";

// ---- ขา ----
const int LED_PIN = 18;
const int BUZZER_PIN = 26;
const int KNOB_PIN = 36;
const int TEMP_PIN = 32;  // ZX-MCP9701
const int SOIL_PIN = 33;  // ZX-SOIL

WiFiClient net;
PubSubClient mqtt(net);

String nodeId, topicTelemetry, topicStatus, topicCmd;
String lotId = "L-001";
unsigned long publishMs = 5000;
unsigned long seq = 0;
unsigned long lastPublish = 0, lastMqttTry = 0, lastWifiCheck = 0;
int beepsLeft = 0;

bool timeValid() { return time(nullptr) > 1704067200; }

// ISO 8601 แบบ UTC เช่น 2026-11-17T07:05:09Z (ฝั่ง Python แปลงเขตเวลาต่อเอง)
String isoTimeUtc() {
  time_t now = time(nullptr);
  struct tm tm;
  gmtime_r(&now, &tm);
  char buf[25];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tm);
  return buf;
}

void onMessage(char *topic, byte *payload, unsigned int len) {
  JsonDocument cmd;
  DeserializationError err = deserializeJson(cmd, payload, len);
  if (err) {
    Serial.printf("cmd JSON ผิดรูปแบบ: %s\n", err.c_str());
    return;
  }
  Serial.print("cmd: ");
  serializeJson(cmd, Serial);
  Serial.println();

  if (cmd["led"].is<bool>()) digitalWrite(LED_PIN, cmd["led"].as<bool>() ? HIGH : LOW);
  if (cmd["beep"].is<int>()) beepsLeft = constrain(cmd["beep"].as<int>(), 0, 10) * 2;
  if (cmd["lot_id"].is<const char *>()) lotId = cmd["lot_id"].as<const char *>();
  if (cmd["interval_ms"].is<unsigned long>())
    publishMs = constrain(cmd["interval_ms"].as<unsigned long>(), 500UL, 600000UL);
  lastPublish = 0;  // ส่งค่าทันทีเพื่อยืนยันว่ารับคำสั่งแล้ว
}

void maintainWifi() {
  if (millis() - lastWifiCheck < 10000) return;
  lastWifiCheck = millis();
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASS);
  }
}

void maintainMqtt() {
  if (mqtt.connected() || WiFi.status() != WL_CONNECTED) return;
  if (millis() - lastMqttTry < 5000) return;  // ลองใหม่ทุก 5 วินาที ไม่ถี่เกินไป
  lastMqttTry = millis();

  Serial.printf("เชื่อม MQTT %s:%d ... ", MQTT_HOST, MQTT_PORT);
  // LWT: ถ้าบอร์ดหายไปเฉย ๆ broker จะประกาศ "offline" แทนให้
  bool ok = mqtt.connect(nodeId.c_str(), MQTT_USER, MQTT_PASS,
                         topicStatus.c_str(), 1, true, "offline");
  if (ok) {
    Serial.println("สำเร็จ");
    mqtt.publish(topicStatus.c_str(), "online", true);
    mqtt.subscribe(topicCmd.c_str(), 1);
  } else {
    Serial.printf("ไม่สำเร็จ (state %d)\n", mqtt.state());
  }
}

void publishTelemetry() {
  int tempMv = analogReadMilliVolts(TEMP_PIN);
  int soilMv = analogReadMilliVolts(SOIL_PIN);

  JsonDocument doc;
  doc["lot_id"] = lotId;
  doc["node_id"] = nodeId;
  if (timeValid()) doc["ts"] = isoTimeUtc();
  else doc["ts"] = nullptr;  // ยังไม่ sync เวลา — ฝั่งรับใช้เวลาที่ได้รับแทน
  doc["seq"] = seq++;
  doc["uptime_ms"] = millis();
  doc["temp_c"] = round((tempMv - 400) / 19.5 * 10) / 10.0;
  doc["soil_mv"] = soilMv;
  doc["knob_mv"] = analogReadMilliVolts(KNOB_PIN);
  doc["rssi"] = WiFi.RSSI();

  char buf[384];
  size_t n = serializeJson(doc, buf);
  bool ok = mqtt.publish(topicTelemetry.c_str(), buf, n);
  Serial.printf("%s %s\n", ok ? "→" : "✗", buf);
}

void updateBeep() {
  static unsigned long last = 0;
  if (beepsLeft == 0 || millis() - last < 150) return;
  last = millis();
  ledcWrite(BUZZER_PIN, beepsLeft % 2 == 0 ? 128 : 0);
  beepsLeft--;
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  ledcAttach(BUZZER_PIN, 2500, 8);

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  configTzTime(TZ_THAILAND, NTP_SERVER);

  // node_id จาก MAC address 3 ไบต์ท้าย ไม่ซ้ำกันในแต่ละบอร์ด
  uint8_t mac[6];
  WiFi.macAddress(mac);
  char id[16];
  snprintf(id, sizeof(id), "esp32-%02x%02x%02x", mac[3], mac[4], mac[5]);
  nodeId = id;
  String base = String("tgr2026/") + TEAM + "/" + nodeId;
  topicTelemetry = base + "/telemetry";
  topicStatus = base + "/status";
  topicCmd = base + "/cmd";
  Serial.printf("node_id = %s\ncmd topic = %s\n", nodeId.c_str(), topicCmd.c_str());

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMessage);
  mqtt.setBufferSize(512);
  mqtt.setKeepAlive(15);
}

void loop() {
  maintainWifi();
  maintainMqtt();
  mqtt.loop();
  updateBeep();

  if (mqtt.connected() && (lastPublish == 0 || millis() - lastPublish >= publishMs)) {
    lastPublish = millis();
    publishTelemetry();
  }
}
