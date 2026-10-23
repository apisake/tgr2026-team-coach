// ตั้งค่าของ L09 — แก้ไฟล์นี้ไฟล์เดียวก่อนอัปโหลด
#pragma once

// ---- เครือข่าย ----
#define WIFI_SSID      "YOUR_SSID"
#define WIFI_PASS      "YOUR_PASSWORD"
#define MQTT_HOST      "192.168.1.10"   // IP ของ Pi ที่รัน Mosquitto
#define MQTT_PORT      1883
#define NTP_SERVER     "pool.ntp.org"   // ไม่มีอินเทอร์เน็ต → IP ของ Pi
#define TEAM           "canet"

// ---- ขา (ตรวจกับผล L00) ----
#define LED_PIN        18   // สถานะ
#define BUTTON_PIN     0    // เริ่ม/หยุดการอบ
#define BUZZER_PIN     26
#define TEMP_PIN       32   // K7 ZX-MCP9701 อุณหภูมิในตู้อบ
#define MOIST_PIN      33   // K8 ZX-SOIL แทนเซ็นเซอร์ความชื้นเมล็ด
#define FAN_PIN        19   // K4 ZX-LED แทนพัดลม (PWM)
#define HEATER_PIN     23   // K5 ZX-LED แทนรีเลย์ฮีตเตอร์
#define SDA_PIN        21
#define SCL_PIN        22

// ---- ค่าเริ่มต้นของการควบคุม (เปลี่ยนได้ทาง MQTT cmd) ----
#define DEFAULT_SETPOINT_C   45.0  // อุณหภูมิอากาศเป้าหมาย — ตรวจกับงานค้นคว้า R3
#define DEFAULT_BAND_C       2.0   // hysteresis: เปิดฮีตเตอร์ < SP−band, ปิด > SP+band
#define DEFAULT_TARGET_PCT   12.0  // ความชื้นเป้าหมาย — ตรวจกับงานค้นคว้า R4
#define TEMP_MAX_C           60.0  // เกินนี้ = FAULT ตัดฮีตเตอร์ทันที
#define FAN_MIN_DUTY         80    // พัดลมหมุนเบา ๆ ตลอดการอบ (0–255)

// ---- calibrate ZX-SOIL (วัดจริงตามบทที่ 5) ----
#define MOIST_DRY_MV   300
#define MOIST_WET_MV   2500

#define PUBLISH_MS     5000
