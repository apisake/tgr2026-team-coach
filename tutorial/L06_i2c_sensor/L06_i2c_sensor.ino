// L06 · I2C: สแกนบัส แล้วอ่าน SHT3x (อุณหภูมิ/ความชื้นสัมพัทธ์) จาก datasheet โดยไม่ใช้ไลบรารี
// ต่อ SHT30/SHT31/SHT35 ที่พอร์ต K2 (I2C) — ใช้บัสเดียวกับ OLED

#include <Wire.h>

const int SDA_PIN = 21;
const int SCL_PIN = 22;
const uint8_t SHT3X_ADDR = 0x44;  // 0x45 ถ้าขา ADDR ต่อ VDD

void scanI2C() {
  Serial.println("สแกน I2C:");
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) Serial.printf("  0x%02X\n", addr);
  }
}

// CRC-8 ตาม datasheet SHT3x: polynomial 0x31, ค่าเริ่ม 0xFF
uint8_t crc8(const uint8_t *data, int len) {
  uint8_t crc = 0xFF;
  for (int i = 0; i < len; i++) {
    crc ^= data[i];
    for (int b = 0; b < 8; b++) crc = (crc & 0x80) ? (crc << 1) ^ 0x31 : crc << 1;
  }
  return crc;
}

// วัดแบบ single shot, high repeatability, ไม่ใช้ clock stretching (คำสั่ง 0x2400)
bool readSht3x(float &tempC, float &rh) {
  Wire.beginTransmission(SHT3X_ADDR);
  Wire.write(0x24);
  Wire.write(0x00);
  if (Wire.endTransmission() != 0) return false;  // ไม่มีอุปกรณ์ตอบ

  delay(16);  // datasheet: high repeatability ใช้เวลาสูงสุด 15.5 ms

  if (Wire.requestFrom(SHT3X_ADDR, (uint8_t)6) != 6) return false;
  uint8_t d[6];
  for (int i = 0; i < 6; i++) d[i] = Wire.read();
  if (crc8(d, 2) != d[2] || crc8(d + 3, 2) != d[5]) return false;  // ข้อมูลเสีย

  uint16_t rawT = (d[0] << 8) | d[1];
  uint16_t rawRH = (d[3] << 8) | d[4];
  tempC = -45 + 175.0 * rawT / 65535.0;
  rh = 100.0 * rawRH / 65535.0;
  return true;
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);
  scanI2C();
}

void loop() {
  static unsigned long last = 0;
  if (millis() - last < 2000) return;
  last = millis();

  float t, rh;
  if (readSht3x(t, rh)) {
    Serial.printf("temp:%.2f,rh:%.1f\n", t, rh);
  } else {
    Serial.println("อ่าน SHT3x ไม่ได้ — ตรวจสาย/แอดเดรส");
  }
}
