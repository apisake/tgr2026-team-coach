// L09 · งานรวม: ตัวควบคุมตู้อบเมล็ดกาแฟ (Drying Controller)
//
//   อ่านอุณหภูมิ + ความชื้น → ควบคุมฮีตเตอร์ (hysteresis) + พัดลม (PWM)
//   → แจ้งเตือน → แสดงบน OLED → ส่ง MQTT พร้อม lot_id + ts → รับคำสั่งจาก service
//
// สถานะ:  IDLE --(ปุ่ม/cmd start)--> DRYING --(ความชื้น ≤ เป้า)--> DONE
//                                     |  อุณหภูมิเกิน/เซ็นเซอร์เสีย
//                                     v
//                                   FAULT --(cmd reset / ปุ่ม)--> IDLE
//
// ตั้งค่าทั้งหมดอยู่ใน config.h

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <U8g2lib.h>
#include <Wire.h>
#include <time.h>
#include <esp_task_wdt.h>
#include "config.h"

enum State { IDLE, DRYING, DONE, FAULT };
const char *STATE_NAME[] = {"idle", "drying", "done", "fault"};

// ---- สถานะของระบบ ----
State state = IDLE;
String lotId = "L-001";
String faultReason;
float setpointC = DEFAULT_SETPOINT_C;
float bandC = DEFAULT_BAND_C;
float targetPct = DEFAULT_TARGET_PCT;

float tempC = NAN, moistPct = NAN;
int tempMv = 0, moistMv = 0;
bool heaterOn = false;
int fanDuty = 0;

// ---- เครือข่าย ----
WiFiClient net;
PubSubClient mqtt(net);
String nodeId, topicTelemetry, topicStatus, topicEvent, topicCmd;
unsigned long seq = 0;
unsigned long lastPublish = 0, lastMqttTry = 0, lastWifiCheck = 0;

U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE, SCL_PIN, SDA_PIN);

// =====================================================================
// เซ็นเซอร์
// =====================================================================

int readMv(int pin) {
  const int N = 9;
  int v[N];
  for (int i = 0; i < N; i++) v[i] = analogReadMilliVolts(pin);
  for (int i = 1; i < N; i++) {
    int x = v[i], j = i - 1;
    while (j >= 0 && v[j] > x) { v[j + 1] = v[j]; j--; }
    v[j + 1] = x;
  }
  return v[N / 2];
}

void readSensors() {
  static float emaT = NAN, emaM = NAN;
  tempMv = readMv(TEMP_PIN);
  moistMv = readMv(MOIST_PIN);
  float t = (tempMv - 400) / 19.5;
  float m = constrain(100.0 * (moistMv - MOIST_DRY_MV) / (MOIST_WET_MV - MOIST_DRY_MV), 0, 100);
  emaT = isnan(emaT) ? t : 0.2 * t + 0.8 * emaT;
  emaM = isnan(emaM) ? m : 0.1 * m + 0.9 * emaM;
  tempC = emaT;
  moistPct = emaM;
}

// MCP9701 ให้ ≥ 400 mV ที่ 0 °C ถ้าต่ำกว่า 150 mV แปลว่าสายหลุด
bool tempSensorOk() { return tempMv > 150 && tempMv < 3000; }

// =====================================================================
// เครือข่าย
// =====================================================================

bool timeValid() { return time(nullptr) > 1704067200; }

String isoTimeUtc() {
  time_t now = time(nullptr);
  struct tm tm;
  gmtime_r(&now, &tm);
  char buf[25];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tm);
  return buf;
}

void addHeader(JsonDocument &doc) {
  doc["lot_id"] = lotId;
  doc["node_id"] = nodeId;
  if (timeValid()) doc["ts"] = isoTimeUtc();
  else doc["ts"] = nullptr;
  doc["seq"] = seq++;
}

void publishJson(const String &topic, JsonDocument &doc) {
  char buf[512];
  size_t n = serializeJson(doc, buf);
  mqtt.publish(topic.c_str(), buf, n);
  Serial.println(buf);
}

void publishTelemetry() {
  if (!mqtt.connected()) return;
  JsonDocument doc;
  addHeader(doc);
  doc["state"] = STATE_NAME[state];
  doc["temp_c"] = round(tempC * 10) / 10.0;
  doc["moist_pct"] = round(moistPct * 10) / 10.0;
  doc["setpoint_c"] = setpointC;
  doc["target_pct"] = targetPct;
  doc["heater"] = heaterOn;
  doc["fan_duty"] = fanDuty;
  doc["rssi"] = WiFi.RSSI();
  doc["uptime_ms"] = millis();
  publishJson(topicTelemetry, doc);
}

// เหตุการณ์สำคัญ (เปลี่ยนสถานะ, fault) ส่งแยก topic เพื่อให้ service บันทึกเป็นประวัติของล็อต
void publishEvent(const char *event, const String &detail = "") {
  if (!mqtt.connected()) return;
  JsonDocument doc;
  addHeader(doc);
  doc["event"] = event;
  doc["state"] = STATE_NAME[state];
  if (detail.length()) doc["detail"] = detail;
  publishJson(topicEvent, doc);
}

// =====================================================================
// การควบคุม
// =====================================================================

void beep(int ms) {
  ledcWrite(BUZZER_PIN, 128);
  delay(ms);  // สั้นมาก ยอมให้บล็อกได้
  ledcWrite(BUZZER_PIN, 0);
}

void setState(State s, const String &detail = "") {
  if (s == state) return;
  state = s;
  if (s == FAULT) faultReason = detail;
  Serial.printf("state → %s %s\n", STATE_NAME[s], detail.c_str());
  publishEvent("state", detail);
  lastPublish = 0;  // ส่ง telemetry ทันที
  beep(s == FAULT ? 400 : 80);
}

void control() {
  if (state == DRYING) {
    if (!tempSensorOk()) setState(FAULT, "temp sensor");
    else if (tempC > TEMP_MAX_C) setState(FAULT, "over temp");
    else if (moistPct <= targetPct) setState(DONE, "target reached");
  }

  if (state == DRYING) {
    // hysteresis: อยู่ในแถบ ±band ให้คงสถานะเดิม ฮีตเตอร์จึงไม่สลับถี่
    if (tempC < setpointC - bandC) heaterOn = true;
    else if (tempC > setpointC + bandC) heaterOn = false;
    // พัดลม: หมุนเบาตลอด และเร่งเมื่อร้อนเกินเป้า (proportional)
    float over = tempC - setpointC;
    fanDuty = constrain(FAN_MIN_DUTY + (int)(over * 40), FAN_MIN_DUTY, 255);
  } else {
    heaterOn = false;
    fanDuty = (state == FAULT && tempC > TEMP_MAX_C) ? 255 : 0;  // ร้อนเกิน → เป่าระบาย
  }

  digitalWrite(HEATER_PIN, heaterOn ? HIGH : LOW);
  ledcWrite(FAN_PIN, fanDuty);
}

void startDrying() {
  if (state == FAULT) return;
  setState(DRYING, "start");
}

void stopDrying() {
  setState(IDLE, "stop");
}

// =====================================================================
// MQTT
// =====================================================================

void onMessage(char *topic, byte *payload, unsigned int len) {
  JsonDocument cmd;
  if (deserializeJson(cmd, payload, len)) {
    publishEvent("cmd_error", "invalid json");
    return;
  }
  if (cmd["lot_id"].is<const char *>()) {
    if (state == DRYING) {
      publishEvent("cmd_error", "stop before changing lot_id");
    } else {
      lotId = cmd["lot_id"].as<const char *>();
      if (state == DONE) setState(IDLE, "new lot");
    }
  }
  if (cmd["setpoint_c"].is<float>()) setpointC = constrain(cmd["setpoint_c"].as<float>(), 25.0f, TEMP_MAX_C - 5);
  if (cmd["band_c"].is<float>()) bandC = constrain(cmd["band_c"].as<float>(), 0.5f, 10.0f);
  if (cmd["target_pct"].is<float>()) targetPct = constrain(cmd["target_pct"].as<float>(), 0.0f, 100.0f);
  if (cmd["start"] == true) startDrying();
  if (cmd["stop"] == true) stopDrying();
  if (cmd["reset"] == true && state == FAULT) setState(IDLE, "reset");
  lastPublish = 0;
}

void maintainNetwork() {
  if (millis() - lastWifiCheck > 10000) {
    lastWifiCheck = millis();
    if (WiFi.status() != WL_CONNECTED) {
      WiFi.disconnect();
      WiFi.begin(WIFI_SSID, WIFI_PASS);
    }
  }
  if (!mqtt.connected() && WiFi.status() == WL_CONNECTED && millis() - lastMqttTry > 5000) {
    lastMqttTry = millis();
    if (mqtt.connect(nodeId.c_str(), nullptr, nullptr, topicStatus.c_str(), 1, true, "offline")) {
      mqtt.publish(topicStatus.c_str(), "online", true);
      mqtt.subscribe(topicCmd.c_str(), 1);
      publishEvent("boot_or_reconnect");
    }
  }
  mqtt.loop();
}

// =====================================================================
// ปุ่มและจอ
// =====================================================================

void handleButton() {
  static bool last = HIGH;
  static unsigned long lastChange = 0;
  bool b = digitalRead(BUTTON_PIN);
  if (b != last && millis() - lastChange > 30) {
    lastChange = millis();
    last = b;
    if (b == LOW) {
      if (state == DRYING) stopDrying();
      else if (state == FAULT) setState(IDLE, "reset");
      else startDrying();
    }
  }
}

void drawScreen() {
  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);

  oled.setCursor(0, 9);
  oled.printf("%-8s %s", lotId.c_str(), STATE_NAME[state]);
  oled.drawStr(98, 9, WiFi.status() == WL_CONNECTED ? (mqtt.connected() ? "MQTT" : "WiFi") : "----");
  oled.drawHLine(0, 12, 128);

  oled.setFont(u8g2_font_logisoso16_tr);
  oled.setCursor(0, 32);
  oled.printf("%.1fC", tempC);
  oled.setCursor(66, 32);
  oled.printf("%.0f%%", moistPct);

  oled.setFont(u8g2_font_6x10_tf);
  oled.setCursor(0, 44);
  oled.printf("SP %.0f+-%.0f", setpointC, bandC);
  oled.setCursor(66, 44);
  oled.printf("TG %.0f%%", targetPct);

  oled.setCursor(0, 58);
  if (state == FAULT) {
    oled.printf("FAULT: %s", faultReason.c_str());
  } else {
    oled.printf("HEAT %s", heaterOn ? "ON " : "off");
    oled.setCursor(66, 58);
    oled.printf("FAN %d%%", fanDuty * 100 / 255);
  }
  oled.sendBuffer();
}

// =====================================================================

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);
  pinMode(HEATER_PIN, OUTPUT);
  digitalWrite(HEATER_PIN, LOW);  // ปลอดภัยไว้ก่อน: ฮีตเตอร์ปิดตอนบูต
  ledcAttach(FAN_PIN, 25000, 8);  // 25 kHz พ้นช่วงที่หูได้ยิน
  ledcAttach(BUZZER_PIN, 2500, 8);

  oled.setI2CAddress(0x3C * 2);
  oled.begin();

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  configTzTime("<+07>-7", NTP_SERVER);

  uint8_t mac[6];
  WiFi.macAddress(mac);
  char id[16];
  snprintf(id, sizeof(id), "esp32-%02x%02x%02x", mac[3], mac[4], mac[5]);
  nodeId = id;
  String base = String("tgr2026/") + TEAM + "/" + nodeId;
  topicTelemetry = base + "/telemetry";
  topicStatus = base + "/status";
  topicEvent = base + "/event";
  topicCmd = base + "/cmd";
  Serial.printf("node_id = %s\n", nodeId.c_str());

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMessage);
  mqtt.setBufferSize(512);
  mqtt.setKeepAlive(15);

  // Watchdog: ถ้า loop() ค้างเกิน 15 วินาที ให้รีเซ็ตบอร์ด (ฮีตเตอร์จะปิดตอนบูต)
  esp_task_wdt_config_t wdt = {.timeout_ms = 15000, .idle_core_mask = 0, .trigger_panic = true};
  if (esp_task_wdt_reconfigure(&wdt) != ESP_OK) esp_task_wdt_init(&wdt);
  esp_task_wdt_add(NULL);

  readSensors();
}

void loop() {
  esp_task_wdt_reset();
  maintainNetwork();
  handleButton();

  static unsigned long lastControl = 0;
  if (millis() - lastControl >= 500) {
    lastControl = millis();
    readSensors();
    control();
    drawScreen();
    // LED: ติดค้าง = กำลังอบ, กระพริบ = fault, ดับ = idle/done
    digitalWrite(LED_PIN, state == DRYING || (state == FAULT && (millis() / 500) % 2));
  }

  if (lastPublish == 0 || millis() - lastPublish >= PUBLISH_MS) {
    lastPublish = millis();
    publishTelemetry();
  }
}
