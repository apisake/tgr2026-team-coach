# บทที่ 0 · ติดตั้ง toolchain และตรวจบอร์ด

เป้าหมาย: ทุกเครื่องในทีมอัปโหลดโค้ดลงบอร์ด IPST-WiFi และเปิด Serial Monitor ได้ และรู้ว่าขาบนบอร์ดของเราตรงกับตารางใน [README](README.md)

## 1. ติดตั้งโปรแกรม

1. ติดตั้ง **Arduino IDE 2.x** จาก <https://www.arduino.cc/en/software>
2. ติดตั้งไดรเวอร์ **CP210x** (บอร์ดใช้ชิป CP2104) จาก <https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers> — Windows 10/11 ส่วนใหญ่ติดตั้งให้อัตโนมัติ macOS รุ่นใหม่ก็มีให้แล้ว
3. เปิด Arduino IDE → **File → Preferences** → ช่อง *Additional boards manager URLs* ใส่
   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```
4. **Tools → Board → Boards Manager** ค้น `esp32` แล้วติดตั้ง **esp32 by Espressif Systems** รุ่น 3.x (บทเรียนนี้ทดสอบกับ 3.3.12)
5. **Tools → Manage Libraries** ติดตั้ง `U8g2`, `ArduinoJson` (7.x), `PubSubClient`

> **Offline-first:** ก่อนออกเดินทาง ให้ทุกเครื่องเปิดและคอมไพล์ทุกสเก็ตช์ในโฟลเดอร์นี้ครั้งหนึ่ง เพื่อให้ core และไลบรารีอยู่ในเครื่องครบ แล้วสำรองโฟลเดอร์ `Arduino15` และ `Documents/Arduino/libraries` ลง USB

## 2. ตั้งค่าบอร์ด

ต่อสาย microUSB เปิดสวิตช์ไฟหลักและสวิตช์ไฟ ESP32 บนบอร์ด แล้วตั้งค่าใน **Tools**:

| ตัวเลือก | ค่า |
|---|---|
| Board | **ESP32 Dev Module** |
| Port | COM ที่ขึ้นเมื่อเสียบบอร์ด (Windows) หรือ `/dev/cu.SLAB_USBtoUART` / `/dev/cu.usbserial-*` (macOS) |
| PSRAM | Enabled (ถ้าจะใช้ PSRAM 4 MB) |
| Upload Speed | 921600 (ถ้าอัปโหลดไม่ผ่านให้ลด 460800 หรือ 115200) |

ถ้าไม่เห็นพอร์ต: เปลี่ยนสาย USB (สายชาร์จอย่างเดียวส่งข้อมูลไม่ได้), ตรวจไดรเวอร์ CP210x, ตรวจว่าเปิดสวิตช์ไฟโมดูล ESP32 แล้ว

ถ้าอัปโหลดขึ้น `Failed to connect to ESP32`: กดปุ่ม **BUTTON (GPIO0) ค้าง** แล้วกด **RESET** หนึ่งครั้ง ปล่อย BUTTON แล้วอัปโหลดใหม่

## 3. อัปโหลดสเก็ตช์ตรวจบอร์ด

เปิด [L00_board_check/L00_board_check.ino](L00_board_check/L00_board_check.ino) อัปโหลด แล้วเปิด **Serial Monitor** ที่ 115200 baud
(ถ้าไม่เห็นข้อความแรก ให้กด RESET บนบอร์ดหลังเปิด Serial Monitor)

สเก็ตช์จะทำตามลำดับ:

1. **LED GPIO18** ติด 1 วินาที — ถ้าไม่ติดแต่ดับแทน แสดงว่า LED ต่อแบบ active-low ให้จดไว้
2. **เสียงที่ 1** ออกจาก GPIO26 แล้ว **เสียงที่ 2** ออกจาก GPIO25 — จดว่าลำโพงบนบอร์ดดังที่เสียงไหน
3. **สแกน I2C** — ควรเจอ OLED ที่ `0x3C` (หรือ `0x3D`)
4. วนแสดง **ค่าแรงดันของขา GPIO36** และสถานะปุ่ม — หมุน KNOB บนบอร์ดแล้วค่าควรเปลี่ยน, กด BUTTON แล้ว LED ควรติด

### จดผลลงตารางนี้ (ทำครั้งเดียวต่อบอร์ด แล้วแชร์ให้ทีม)

| รายการ | ค่าที่คาดไว้ | ผลจริง |
|---|---|---|
| LED ติดเมื่อเขียน `HIGH` | ใช่ | |
| ลำโพงบนบอร์ดอยู่ที่ | GPIO26 (เสียงที่ 1) | |
| แอดเดรส OLED | `0x3C` | |
| KNOB อยู่ที่ GPIO36 | ใช่ (ค่าเปลี่ยนเมื่อหมุน) | |

ถ้าผลต่างจากที่คาดไว้ ให้แก้ `BUZZER_PIN`, `OUT_PIN`, `KNOB_PIN` หรือ `OLED` ที่หัวไฟล์ของสเก็ตช์บทถัดไป และแก้ตารางใน [README](README.md) ด้วย

## ข้อควรระวังของ ESP32

- ลอจิก **3.3 V** — ห้ามป้อน 5 V เข้าขาสัญญาณ
- **Strapping pins** 0, 2, 5, 12, 15 กำหนดโหมดตอนบูต: อย่าต่ออุปกรณ์ที่ดึงขาเหล่านี้ HIGH/LOW ค้างไว้ตอนรีเซ็ต (โดยเฉพาะ GPIO12 ต้องเป็น LOW ตอนบูต)
- **GPIO34–39** เป็น input อย่างเดียวและไม่มี pull-up/pull-down ภายใน
- **ADC2** (GPIO0, 2, 4, 12–15, 25–27) ใช้อ่าน analog ไม่ได้ขณะเปิด Wi-Fi — บอร์ดนี้ให้พอร์ต analog เป็น ADC1 (GPIO32–36) อยู่แล้ว
