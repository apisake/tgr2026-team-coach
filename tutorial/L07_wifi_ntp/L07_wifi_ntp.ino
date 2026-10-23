// L07 · Wi-Fi + reconnect แบบไม่บล็อก + เวลาจาก NTP
// แก้ WIFI_SSID / WIFI_PASS / NTP_SERVER ก่อนอัปโหลด

#include <WiFi.h>
#include <time.h>
#include <U8g2lib.h>
#include <Wire.h>

const char *WIFI_SSID = "YOUR_SSID";
const char *WIFI_PASS = "YOUR_PASSWORD";
// ไม่มีอินเทอร์เน็ต → ใช้ IP ของ Pi/notebook ที่รัน NTP server (เช่น chrony) แทน
const char *NTP_SERVER = "pool.ntp.org";
const char *NTP_SERVER2 = "time.navy.mi.th";
const char *TZ_THAILAND = "<+07>-7";  // POSIX TZ: UTC+7

const int LED_PIN = 18;
const int SDA_PIN = 21;
const int SCL_PIN = 22;

U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE, SCL_PIN, SDA_PIN);

unsigned long lastWifiCheck = 0;

void startWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
}

// ตรวจทุก 10 วินาที ถ้าหลุดนานให้สั่งเชื่อมใหม่ โดยไม่หยุดรอ
void maintainWifi() {
  if (millis() - lastWifiCheck < 10000) return;
  lastWifiCheck = millis();
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi หลุด กำลังเชื่อมใหม่...");
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASS);
  }
}

// เวลาถูกต้องเมื่อปีมากกว่า 2024 (ก่อน sync นาฬิกาจะเริ่มที่ปี 1970)
bool timeValid() {
  return time(nullptr) > 1704067200;  // 2024-01-01T00:00:00Z
}

// เวลาท้องถิ่นแบบ ISO 8601 เช่น 2026-11-17T14:05:09+07:00
String isoTime() {
  if (!timeValid()) return "";
  time_t now = time(nullptr);
  struct tm tm;
  localtime_r(&now, &tm);
  char buf[32];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%S%z", &tm);  // +0700
  String s(buf);
  s = s.substring(0, s.length() - 2) + ":" + s.substring(s.length() - 2);  // → +07:00
  return s;
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  oled.setI2CAddress(0x3C * 2);
  oled.begin();

  startWifi();
  // ตั้งค่า SNTP ครั้งเดียว ระบบจะ sync เองเมื่อมีเครือข่าย และ sync ซ้ำทุก 1 ชม.
  configTzTime(TZ_THAILAND, NTP_SERVER, NTP_SERVER2);
}

void loop() {
  maintainWifi();

  bool online = WiFi.status() == WL_CONNECTED;
  digitalWrite(LED_PIN, online || (millis() / 150) % 2 ? HIGH : LOW);  // กระพริบเร็ว = ยังไม่ต่อ

  static unsigned long last = 0;
  if (millis() - last < 500) return;
  last = millis();

  String ts = isoTime();
  Serial.printf("wifi=%s ip=%s rssi=%d ts=%s\n", online ? "ok" : "down",
                WiFi.localIP().toString().c_str(), online ? WiFi.RSSI() : 0,
                ts.length() ? ts.c_str() : "(ยังไม่ sync)");

  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);
  oled.setCursor(0, 10);
  oled.printf("WiFi: %s", online ? WIFI_SSID : "connecting...");
  oled.setCursor(0, 22);
  if (online) oled.printf("%s  %ddBm", WiFi.localIP().toString().c_str(), WiFi.RSSI());
  oled.drawHLine(0, 26, 128);
  if (timeValid()) {
    oled.setFont(u8g2_font_logisoso22_tn);
    oled.setCursor(0, 54);
    oled.print(ts.substring(11, 19));  // HH:MM:SS
    oled.setFont(u8g2_font_6x10_tf);
    oled.setCursor(0, 64);
    oled.print(ts.substring(0, 10));   // YYYY-MM-DD
  } else {
    oled.drawStr(0, 44, "waiting for NTP...");
  }
  oled.sendBuffer();
}
