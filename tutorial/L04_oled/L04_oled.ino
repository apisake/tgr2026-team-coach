// L04 · จอ OLED 0.96" (SSD1306, I2C) ด้วยไลบรารี U8g2
// แสดงค่า KNOB เป็นตัวเลข + แถบกราฟ + เวลาที่บอร์ดทำงาน

#include <U8g2lib.h>
#include <Wire.h>

const int SDA_PIN = 21;
const int SCL_PIN = 22;
const int KNOB_PIN = 36;

// F = full buffer (ใช้ RAM 1 KB วาดทั้งจอแล้วส่งครั้งเดียว)
U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE, SCL_PIN, SDA_PIN);

void setup() {
  Serial.begin(115200);
  oled.setI2CAddress(0x3C * 2);  // U8g2 ใช้แอดเดรสแบบ 8 บิต
  oled.begin();
  oled.setContrast(200);
}

void loop() {
  static unsigned long last = 0;
  if (millis() - last < 100) return;  // อัปเดตจอ 10 ครั้ง/วินาที
  last = millis();

  int mv = analogReadMilliVolts(KNOB_PIN);
  unsigned long sec = millis() / 1000;

  oled.clearBuffer();

  oled.setFont(u8g2_font_6x10_tf);
  oled.drawStr(0, 10, "IPST-WiFi  KNOB");
  oled.drawHLine(0, 13, 128);

  oled.setFont(u8g2_font_logisoso22_tn);
  oled.setCursor(0, 42);
  oled.print(mv);
  oled.setFont(u8g2_font_6x10_tf);
  oled.drawStr(70, 42, "mV");

  // แถบกราฟ 0–3300 mV
  int w = map(constrain(mv, 0, 3300), 0, 3300, 0, 124);
  oled.drawFrame(0, 48, 128, 8);
  oled.drawBox(2, 50, w, 4);

  oled.setCursor(0, 64);
  oled.printf("up %02lu:%02lu:%02lu", sec / 3600, (sec / 60) % 60, sec % 60);

  oled.sendBuffer();
}
