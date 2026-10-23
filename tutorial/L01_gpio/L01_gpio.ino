// L01 · GPIO: LED กระพริบแบบไม่บล็อก + ปุ่มกดพร้อม debounce
// กด BUTTON เพื่อสลับโหมด: กระพริบช้า → กระพริบเร็ว → ดับ

const int LED_PIN = 18;
const int BUTTON_PIN = 0;  // กด = LOW (pull-up บนบอร์ด)

const unsigned long DEBOUNCE_MS = 30;
const unsigned long BLINK_MS[] = {500, 100, 0};  // 0 = ดับ
const char *MODE_NAME[] = {"ช้า", "เร็ว", "ดับ"};

int mode = 0;
bool ledOn = false;
unsigned long lastBlink = 0;

// สถานะปุ่มสำหรับ debounce
bool stableState = HIGH;
bool lastReading = HIGH;
unsigned long lastChange = 0;

// คืนค่า true ครั้งเดียวต่อการกดหนึ่งครั้ง
bool buttonPressed() {
  bool reading = digitalRead(BUTTON_PIN);
  if (reading != lastReading) {
    lastChange = millis();
    lastReading = reading;
  }
  if (millis() - lastChange > DEBOUNCE_MS && reading != stableState) {
    stableState = reading;
    return stableState == LOW;
  }
  return false;
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);
  Serial.println("L01 GPIO — กด BUTTON เพื่อเปลี่ยนโหมด");
}

void loop() {
  if (buttonPressed()) {
    mode = (mode + 1) % 3;
    Serial.printf("โหมด: %s\n", MODE_NAME[mode]);
  }

  unsigned long now = millis();
  if (BLINK_MS[mode] == 0) {
    ledOn = false;
  } else if (now - lastBlink >= BLINK_MS[mode]) {
    lastBlink = now;
    ledOn = !ledOn;
  }
  digitalWrite(LED_PIN, ledOn ? HIGH : LOW);
}
