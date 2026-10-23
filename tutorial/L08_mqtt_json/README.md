# บทที่ 8 · MQTT + JSON

บทนี้คือ "ESP32 → Mosquitto บน Pi ส่งข้อมูลได้" ซึ่งเป็นเป้าหมายของ ส. 24 ต.ค. ในแผน

## เรียนอะไร

- **MQTT** = publish/subscribe ผ่าน broker (Mosquitto บน Pi) ผู้ส่งไม่ต้องรู้ว่าใครรับ
- **Topic** ที่ใช้ในบทนี้ (ปรับให้ตรงกับ **Data Contract v1** ของทีม):

  | Topic | ทิศทาง | เนื้อหา |
  |---|---|---|
  | `tgr2026/<team>/<node_id>/telemetry` | ESP32 → broker | JSON ค่าเซ็นเซอร์ ทุก 5 วินาที |
  | `tgr2026/<team>/<node_id>/status` | ESP32 → broker | `online` / `offline` (retain) |
  | `tgr2026/<team>/<node_id>/cmd` | broker → ESP32 | JSON คำสั่ง |

- **ทุกข้อความต้องมี `lot_id` + `ts`** (หลักใน C1 ของแผน) — `lot_id` เชื่อมข้อมูลจาก sensor, vision และตลาดเข้าด้วยกัน ถ้ายังไม่ sync เวลา ให้ส่ง `ts: null` ไม่ใช่ปี 1970
- ใส่ `seq` (เลขลำดับ) และ `uptime_ms` ด้วย ฝั่งรับจะรู้ว่า **ข้อความหาย** หรือ **บอร์ดรีเซ็ต** (seq กลับเป็น 0)
- **LWT (Last Will and Testament)**: บอกล่วงหน้าตอน connect ว่า "ถ้าฉันหายไปเฉย ๆ ให้ประกาศ `offline` ที่ topic status" — dashboard จึงรู้ว่า node ไหนตาย
- **Retain**: broker เก็บข้อความล่าสุดของ topic ไว้ ผู้ที่ subscribe ทีหลังได้รับทันที (เหมาะกับ status ไม่เหมาะกับ telemetry)
- **QoS**: PubSubClient **publish ได้แค่ QoS 0** แต่ subscribe เป็น QoS 1 ได้ ถ้าต้องการ publish QoS 1 ให้ใช้ไลบรารี `esp-mqtt` ของ ESP-IDF (`#include "mqtt_client.h"`)
- **ArduinoJson 7**: ใช้ `JsonDocument` ตัวเดียว (ไม่ต้องกำหนดขนาดแบบ v6), `doc["key"].is<T>()` ตรวจชนิดก่อนอ่าน — **คำสั่งที่ผิดรูปแบบต้องไม่ทำให้บอร์ดค้าง**
- `mqtt.setBufferSize(512)` — ค่าเริ่มต้น 256 ไบต์ ข้อความ JSON ที่ยาวกว่านั้นจะ publish ไม่ออก**โดยไม่มี error ให้เห็น**

## เตรียม broker

บน Pi (หรือ notebook) ที่มี Docker:

```bash
mkdir -p mosquitto && printf "listener 1883\nallow_anonymous true\n" > mosquitto/mosquitto.conf
```

```bash
docker run -d --name mosquitto -p 1883:1883 -v "$PWD/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf" eclipse-mosquitto:2
```

> `allow_anonymous true` ใช้สำหรับซ้อมในเครือข่ายของทีมเท่านั้น

## ลองทำ

1. แก้ `WIFI_SSID`, `WIFI_PASS`, `MQTT_HOST` (IP ของ Pi) และ `TEAM` ใน [L08_mqtt_json.ino](L08_mqtt_json.ino) แล้วอัปโหลด — Serial Monitor จะแสดง `node_id` และ cmd topic
2. ดูข้อมูลจากเครื่องที่มี `mosquitto_sub`:
   ```bash
   mosquitto_sub -h 192.168.1.10 -t "tgr2026/#" -v
   ```
3. ส่งคำสั่ง (แทน `esp32-xxxxxx` ด้วย node_id จริง):
   ```bash
   mosquitto_pub -h 192.168.1.10 -t "tgr2026/canet/esp32-xxxxxx/cmd" -m '{"beep":2,"led":true,"lot_id":"L-002"}'
   ```
   บอร์ดจะดัง 2 ครั้ง ติด LED และส่ง telemetry ทันทีด้วย `lot_id` ใหม่
4. **ทดสอบ LWT:** ถอดสาย USB ของบอร์ด — ภายใน ~20 วินาที (keepalive 15 วินาที × 1.5) `mosquitto_sub` จะเห็น `status offline`
5. **ทดสอบความทน:** หยุด broker (`docker stop mosquitto`) 30 วินาทีแล้วเปิดใหม่ — บอร์ดต้องกลับมาส่งเองได้

ตัวอย่าง telemetry:
```json
{"lot_id":"L-001","node_id":"esp32-a1b2c3","ts":"2026-11-17T07:05:09Z","seq":42,"uptime_ms":210345,"temp_c":31.4,"soil_mv":1210,"knob_mv":1650,"rssi":-58}
```

## แบบฝึกหัด

1. เพิ่ม `soil_pct` ที่ calibrate แล้วจากบทที่ 5 และส่งเฉพาะค่าที่ผ่าน median filter
2. เพิ่มคำสั่ง `{"calibrate":"dry"}` / `{"calibrate":"wet"}` ให้บอร์ดจำค่า ZX-SOIL ปัจจุบันเป็นจุด calibrate (เก็บถาวรด้วย `Preferences` เพื่อไม่หายตอนรีเซ็ต)
3. ถ้า MQTT หลุด ให้ **เก็บข้อความไว้ในบัฟเฟอร์วงกลม** (เช่น 50 ข้อความ) แล้วส่งย้อนหลังเมื่อกลับมาเชื่อมต่อ — `ts` ต้องเป็นเวลาที่วัด ไม่ใช่เวลาที่ส่ง
4. เขียน Python script (paho-mqtt) บน notebook ที่ subscribe `telemetry` แล้วพิมพ์เตือนเมื่อ `seq` ขาดหาย หรือเมื่อ node ใดไม่ส่งข้อมูลเกิน 3 รอบ
