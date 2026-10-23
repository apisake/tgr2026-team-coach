# Tutorial: Arduino + ESP32 บนบอร์ด IPST-WiFi (INEX)

ชุดบทเรียนสำหรับ **C1 — Embedded: ESP32 + Sensor** ใน [TGR2026-Coach-Plan.md](../TGR2026-Coach-Plan.md) ใช้บอร์ด IPST-WiFi ของ INEX ที่มีอยู่ เขียนด้วย Arduino (C/C++)
เป้าหมายคือให้ทุกคนในทีมทำรายการใน Go / No-Go ได้: **ต่อเซ็นเซอร์ใหม่ + ส่ง MQTT ภายใน 30 นาที**

## ลำดับบทเรียน

| บท | โฟลเดอร์ | เรื่อง | เวลา | ผูกกับแผน |
|---|---|---|---|---|
| 0 | [00-setup.md](00-setup.md) · `L00_board_check` | ติดตั้ง toolchain, อัปโหลดครั้งแรก, ตรวจบอร์ด | 45 นาที | ศ. 23 ต.ค. |
| 1 | [L01_gpio](L01_gpio/README.md) | LED, ปุ่ม, debounce, `millis()` แบบไม่บล็อก | 30 นาที | ศ. 23 ต.ค. |
| 2 | [L02_pwm_buzzer](L02_pwm_buzzer/README.md) | LEDC PWM, ปรับความสว่าง, เสียงแจ้งเตือน | 30 นาที | ศ. 23 ต.ค. |
| 3 | [L03_adc](L03_adc/README.md) | ADC1, `analogReadMilliVolts()`, filter, Serial Plotter | 45 นาที | ศ. 23 ต.ค. |
| 4 | [L04_oled](L04_oled/README.md) | จอ OLED I2C ด้วย U8g2 | 30 นาที | ศ. 23 ต.ค. |
| 5 | [L05_zx_sensors](L05_zx_sensors/README.md) | ZX-MCP9701 (อุณหภูมิ), ZX-SOIL (ความชื้น), ZX-SWITCH01, ZX-LED | 60 นาที | ศ. 23 ต.ค. (sensor 2 ชนิด) |
| 6 | [L06_i2c_sensor](L06_i2c_sensor/README.md) | I2C scanner, อ่านเซ็นเซอร์จาก datasheet (SHT3x) | 60 นาที | Phase 1 |
| 7 | [L07_wifi_ntp](L07_wifi_ntp/README.md) | Wi-Fi + reconnect, NTP, เวลาแบบ ISO 8601 | 45 นาที | ส. 24 ต.ค. |
| 8 | [L08_mqtt_json](L08_mqtt_json/README.md) | MQTT + ArduinoJson, `lot_id` + `ts`, LWT, รับคำสั่ง | 60 นาที | ส. 24 ต.ค. |
| 9 | [L09_drying_controller](L09_drying_controller/README.md) | **งานรวม:** ตัวควบคุมการอบเมล็ดกาแฟ (hysteresis + PWM + แจ้งเตือน + MQTT + watchdog) | 2–3 ชม. | Phase 1 (firmware template) |

แต่ละบทมี `README.md` (อธิบาย + แบบฝึกหัด) และสเก็ตช์ `.ino` ที่คอมไพล์ผ่านแล้วกับ ESP32 Arduino core 3.3.x
เปิดสเก็ตช์ใน Arduino IDE ด้วย **File → Open** แล้วเลือกไฟล์ `.ino` ในโฟลเดอร์นั้น

## แผนผังบอร์ด IPST-WiFi

ที่มา: หน้าสินค้า [IPST-WiFi Activity Kit](https://inex.co.th/home/product/ipst-wifi-activity-kit/) และ [เอกสารประกอบชุด (PDF)](https://inex.co.th/store/manual/ipstWiFi-ActivityKit_Info.pdf) ของ INEX
บอร์ดใช้โมดูล **TTGO T8 V1.7** (ESP32 dual-core, flash 4 MB, PSRAM 4 MB) ผ่านชิป USB-serial **CP2104**

| ส่วน | GPIO | หมายเหตุ |
|---|---|---|
| LED ทดสอบ (LED2) | 18 | |
| ปุ่ม BUTTON (SW2) | 0 | มี pull-up 4.7k บนบอร์ด → กด = `LOW` · เป็น strapping pin: **ห้ามกดค้างตอนรีเซ็ต** (จะเข้าโหมดอัปโหลด) |
| ปุ่ม RESET (SW1) | EN | |
| ลำโพง piezo (SP1) | 26 * | |
| พอร์ตเอาต์พุต analog/digital | 25 * | DAC |
| ปุ่มหมุน KNOB (VR1) | 36 (VP) | อ่าน analog, input-only * |
| OLED 0.96" 128×64 | SDA 21, SCL 22 | ชิป SSD1306 ที่แอดเดรส `0x3C` (ยืนยันด้วย I2C scanner ใน L00) |
| K2 พอร์ต I2C | SDA 21, SCL 22 | ใช้บัสเดียวกับ OLED |
| K3 / K4 / K5 | 5 / 19 / 23 | digital I/O (GPIO5 เป็น strapping pin แต่ใช้ได้ปกติ) |
| K7 / K8 / K9 / K10 | 32 / 33 / 34 / 35 | analog in (INEX เรียก ADC4–ADC7) · เป็น **ADC1 ทั้งหมด** จึงใช้ได้ตอนเปิด Wi-Fi · 34, 35 เป็น input-only ไม่มี pull-up |
| microSD | CS 13, SCK 14, MOSI 15, MISO 2 | GPIO2, 12, 15 เป็น strapping pin |
| LED RGB WS2812 ×3 | ยังไม่ทราบ | ไม่ได้ใช้ในบทเรียนนี้ |
| ไฟเลี้ยง | | DC jack 5–9 V (adapter 6 V 2 A) หรือ microUSB หรือแบตเตอรี่ Li-Po 3.7 V · มีสวิตช์ไฟหลักและสวิตช์ไฟโมดูล ESP32 |

\* **ต้องยืนยันกับบอร์ดจริง:** ข้อความของ INEX บอกว่าลำโพงอยู่ที่ GPIO26 และพอร์ตเอาต์พุตอยู่ที่ GPIO25 แต่ป้ายในวงจรของ PDF ดูเหมือนสลับกัน ส่วนปุ่มหมุนอ่านจากป้าย `KNOB-VP` ในวงจร สเก็ตช์ `L00_board_check` จะทดสอบให้รู้ว่าขาไหนคือขาไหน ถ้าผลต่างจากตารางให้แก้ค่าคงที่ที่หัวไฟล์ของทุกสเก็ตช์

พอร์ต JST 3 ขา (S, +, GND) ใช้กับบอร์ด ZX ของ INEX ได้ทันที **ทุกขาของ ESP32 เป็นลอจิก 3.3 V ห้ามป้อน 5 V เข้าขาสัญญาณ**

## ไลบรารีที่ใช้

| ไลบรารี | ใช้ในบท | ติดตั้งจาก Library Manager |
|---|---|---|
| U8g2 (olikraus) | 4, 5, 7, 9 | ค้น `U8g2` |
| ArduinoJson 7.x (Benoit Blanchon) | 8, 9 | ค้น `ArduinoJson` |
| PubSubClient (Nick O'Leary) | 8, 9 | ค้น `PubSubClient` |

`WiFi`, `Wire`, `esp_task_wdt` มาพร้อม ESP32 core
