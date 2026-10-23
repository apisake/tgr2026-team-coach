// L00 · ตรวจบอร์ด IPST-WiFi: LED, ลำโพง, I2C, ปุ่มหมุน, ปุ่มกด
// เปิด Serial Monitor ที่ 115200 แล้วจดผลตามตารางใน 00-setup.md

#include <Wire.h>

const int LED_PIN = 18;
const int BUTTON_PIN = 0;   // กด = LOW
const int KNOB_PIN = 36;    // VP
const int SDA_PIN = 21;
const int SCL_PIN = 22;
const int BUZZER_CANDIDATES[] = {26, 25};

void beep(int pin, int freq, int ms) {
  ledcAttach(pin, freq, 8);
  ledcWrite(pin, 128);  // duty 50%
  delay(ms);
  ledcWrite(pin, 0);
  ledcDetach(pin);
}

void scanI2C() {
  int found = 0;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.printf("  พบอุปกรณ์ที่ 0x%02X\n", addr);
      found++;
    }
  }
  if (found == 0) Serial.println("  ไม่พบอุปกรณ์ I2C");
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== IPST-WiFi board check ===");

  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);  // มี pull-up บนบอร์ดแล้ว

  Serial.println("[1] LED GPIO18 = HIGH 1 วินาที (ติดหรือไม่?)");
  digitalWrite(LED_PIN, HIGH);
  delay(1000);
  digitalWrite(LED_PIN, LOW);

  for (int i = 0; i < 2; i++) {
    int pin = BUZZER_CANDIDATES[i];
    Serial.printf("[2.%d] เสียงที่ %d จาก GPIO%d\n", i + 1, i + 1, pin);
    beep(pin, 2000, 400);
    delay(800);
  }

  Serial.println("[3] สแกน I2C (SDA 21, SCL 22)");
  Wire.begin(SDA_PIN, SCL_PIN);
  scanI2C();

  Serial.println("[4] หมุน KNOB และกด BUTTON — ค่าจะแสดงทุก 0.3 วินาที");
}

void loop() {
  int mv = analogReadMilliVolts(KNOB_PIN);
  bool pressed = digitalRead(BUTTON_PIN) == LOW;
  digitalWrite(LED_PIN, pressed ? HIGH : LOW);
  Serial.printf("knob(GPIO%d) = %4d mV   button = %s\n", KNOB_PIN, mv, pressed ? "กด" : "-");
  delay(300);
}
