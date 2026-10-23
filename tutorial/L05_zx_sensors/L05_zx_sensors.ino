// L05 · เซ็นเซอร์ในชุด IPST-WiFi Activity Kit
//   K7 GPIO32  ZX-MCP9701  อุณหภูมิ
//   K8 GPIO33  ZX-SOIL     ความชื้น (แปลงเป็น % ด้วยค่า calibrate)
//   K3 GPIO5   ZX-SWITCH01 กด = LOW
//   K5 GPIO23  ZX-LED      HIGH = ติด
// ติด ZX-LED + เสียงเตือนเมื่ออุณหภูมิเกิน TEMP_ALARM_C

#include <U8g2lib.h>
#include <Wire.h>

const int TEMP_PIN = 32;
const int SOIL_PIN = 33;
const int SWITCH_PIN = 5;
const int ZXLED_PIN = 23;
const int BUZZER_PIN = 26;
const int SDA_PIN = 21;
const int SCL_PIN = 22;

// ค่า calibrate ZX-SOIL: วัดจริงตอนแห้งและตอนจุ่มน้ำ แล้วแก้สองค่านี้
int soilDryMv = 300;
int soilWetMv = 2500;

const float TEMP_ALARM_C = 40.0;

U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE, SCL_PIN, SDA_PIN);

// อ่าน n ครั้งแล้วคืน median ของค่า mV
int readMv(int pin, int n = 9) {
  int v[15];
  n = constrain(n, 1, 15);
  for (int i = 0; i < n; i++) v[i] = analogReadMilliVolts(pin);
  for (int i = 1; i < n; i++) {
    int x = v[i], j = i - 1;
    while (j >= 0 && v[j] > x) { v[j + 1] = v[j]; j--; }
    v[j + 1] = x;
  }
  return v[n / 2];
}

// MCP9701: Vout = 400 mV + 19.5 mV/°C
float mcp9701C(int mv) {
  return (mv - 400) / 19.5;
}

// แปลง mV เป็น % ตามจุด calibrate (ใช้ได้ทั้งกรณีเปียกแล้วแรงดันขึ้นหรือลง)
float soilPercent(int mv) {
  float pct = 100.0 * (mv - soilDryMv) / (soilWetMv - soilDryMv);
  return constrain(pct, 0, 100);
}

void setup() {
  Serial.begin(115200);
  pinMode(SWITCH_PIN, INPUT_PULLUP);
  pinMode(ZXLED_PIN, OUTPUT);
  ledcAttach(BUZZER_PIN, 2500, 8);
  oled.setI2CAddress(0x3C * 2);
  oled.begin();
  Serial.println("กด ZX-SWITCH01 ค้างไว้เพื่อดูค่า mV ของ ZX-SOIL สำหรับ calibrate");
}

void loop() {
  static unsigned long last = 0;
  if (millis() - last < 500) return;
  last = millis();

  int tMv = readMv(TEMP_PIN);
  int sMv = readMv(SOIL_PIN);
  float tempC = mcp9701C(tMv);
  float soil = soilPercent(sMv);
  bool calMode = digitalRead(SWITCH_PIN) == LOW;
  bool alarm = tempC > TEMP_ALARM_C;

  digitalWrite(ZXLED_PIN, alarm ? HIGH : LOW);
  ledcWrite(BUZZER_PIN, alarm && (millis() / 500) % 2 ? 128 : 0);

  Serial.printf("temp:%.1f,soil_pct:%.0f,temp_mv:%d,soil_mv:%d\n", tempC, soil, tMv, sMv);

  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);
  oled.drawStr(0, 10, calMode ? "CALIBRATE (raw mV)" : "ZX sensors");
  oled.drawHLine(0, 13, 128);
  oled.setFont(u8g2_font_logisoso16_tr);
  oled.setCursor(0, 36);
  if (calMode) oled.printf("T %d", tMv);
  else oled.printf("%.1f C", tempC);
  oled.setCursor(0, 60);
  if (calMode) oled.printf("S %d", sMv);
  else oled.printf("%.0f %%", soil);
  if (alarm) {
    oled.setFont(u8g2_font_6x10_tf);
    oled.drawStr(92, 36, "HOT!");
  }
  oled.sendBuffer();
}
