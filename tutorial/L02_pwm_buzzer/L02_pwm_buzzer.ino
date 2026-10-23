// L02 · PWM ด้วย LEDC: หรี่ไฟ LED และเสียงแจ้งเตือนจาก piezo
// ใช้ API ของ ESP32 Arduino core 3.x: ledcAttach / ledcWrite / ledcWriteTone

const int LED_PIN = 18;
const int EXT_LED_PIN = 19;  // ZX-LED ที่พอร์ต K4 (ถ้ามี)
const int BUZZER_PIN = 26;   // ยืนยันด้วย L00 ก่อน
const int BUTTON_PIN = 0;

const int PWM_FREQ = 5000;  // Hz
const int PWM_BITS = 8;     // duty 0–255

// รูปแบบเสียง: ความถี่ (Hz), เวลาดัง (ms), เวลาเงียบ (ms)
struct Tone { int freq; int onMs; int offMs; };
const Tone ALARM[] = {{2500, 150, 100}, {2500, 150, 100}, {2500, 150, 600}};
const int ALARM_LEN = sizeof(ALARM) / sizeof(ALARM[0]);

// ตัวเล่นเสียงแบบไม่บล็อก
int toneIndex = -1;  // -1 = ไม่ได้เล่น
bool toneOn = false;
unsigned long toneSince = 0;

void startAlarm() {
  toneIndex = 0;
  toneOn = true;
  toneSince = millis();
  ledcWriteTone(BUZZER_PIN, ALARM[0].freq);
}

void updateAlarm() {
  if (toneIndex < 0) return;
  const Tone &t = ALARM[toneIndex];
  unsigned long elapsed = millis() - toneSince;
  if (toneOn && elapsed >= (unsigned long)t.onMs) {
    ledcWriteTone(BUZZER_PIN, 0);  // ความถี่ 0 = เงียบ
    toneOn = false;
    toneSince = millis();
  } else if (!toneOn && elapsed >= (unsigned long)t.offMs) {
    toneIndex++;
    if (toneIndex >= ALARM_LEN) {
      toneIndex = -1;
      return;
    }
    ledcWriteTone(BUZZER_PIN, ALARM[toneIndex].freq);
    toneOn = true;
    toneSince = millis();
  }
}

// หรี่ไฟขึ้นลงแบบสามเหลี่ยม คาบ 2 วินาที
int fadeDuty() {
  unsigned long phase = millis() % 2000;
  int d = phase < 1000 ? phase : 2000 - phase;  // 0..1000..0
  return map(d, 0, 1000, 0, 255);
}

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT);
  ledcAttach(LED_PIN, PWM_FREQ, PWM_BITS);
  ledcAttach(EXT_LED_PIN, PWM_FREQ, PWM_BITS);
  ledcAttach(BUZZER_PIN, 2000, PWM_BITS);
  Serial.println("L02 PWM — กด BUTTON เพื่อเล่นเสียงแจ้งเตือน");
}

void loop() {
  int duty = fadeDuty();
  ledcWrite(LED_PIN, duty);
  ledcWrite(EXT_LED_PIN, 255 - duty);

  static bool lastBtn = HIGH;
  bool btn = digitalRead(BUTTON_PIN);
  if (lastBtn == HIGH && btn == LOW && toneIndex < 0) startAlarm();
  lastBtn = btn;

  updateAlarm();
}
