// L03 · ADC: อ่านแรงดันจาก KNOB และ ZX-POT แล้วกรองสัญญาณ
// เปิด Tools → Serial Plotter (115200) เพื่อดูกราฟ raw / median / ema

const int KNOB_PIN = 36;  // KNOB บนบอร์ด (VP)
const int POT_PIN = 32;   // ZX-POT ที่พอร์ต K7

const int SAMPLE_MS = 20;    // อ่านทุก 20 ms (50 ครั้ง/วินาที)
const int MEDIAN_N = 9;      // จำนวนค่าใน median filter (เลขคี่)
const float EMA_ALPHA = 0.1; // 0..1 ยิ่งน้อยยิ่งเรียบแต่ตอบสนองช้า

int window[MEDIAN_N];
int windowPos = 0;
float ema = -1;

int median(const int *data, int n) {
  int sorted[MEDIAN_N];
  memcpy(sorted, data, n * sizeof(int));
  // insertion sort พอสำหรับ n เล็ก
  for (int i = 1; i < n; i++) {
    int v = sorted[i], j = i - 1;
    while (j >= 0 && sorted[j] > v) { sorted[j + 1] = sorted[j]; j--; }
    sorted[j + 1] = v;
  }
  return sorted[n / 2];
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);                     // 0–4095
  analogSetPinAttenuation(KNOB_PIN, ADC_11db);  // ช่วงวัดประมาณ 0–3.1 V
  analogSetPinAttenuation(POT_PIN, ADC_11db);
  for (int i = 0; i < MEDIAN_N; i++) window[i] = analogReadMilliVolts(KNOB_PIN);
}

void loop() {
  static unsigned long last = 0;
  if (millis() - last < SAMPLE_MS) return;
  last = millis();

  int raw = analogRead(KNOB_PIN);          // ค่าดิบ 0–4095 (ไม่ได้ calibrate)
  int mv = analogReadMilliVolts(KNOB_PIN); // mV ที่ผ่าน calibration จาก eFuse

  window[windowPos] = mv;
  windowPos = (windowPos + 1) % MEDIAN_N;
  int med = median(window, MEDIAN_N);

  ema = (ema < 0) ? med : EMA_ALPHA * med + (1 - EMA_ALPHA) * ema;

  int potMv = analogReadMilliVolts(POT_PIN);

  // รูปแบบ label:value ที่ Serial Plotter ของ IDE 2.x อ่านได้
  Serial.printf("raw_x0.8:%d,mv:%d,median:%d,ema:%.0f,pot_mv:%d\n",
                (int)(raw * 0.8), mv, med, ema, potMv);
}
