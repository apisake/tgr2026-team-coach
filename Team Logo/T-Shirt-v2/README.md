# T-Shirt v2

รอบออกแบบเสื้อรอบใหม่ แยกจากงานเดิมใน `Team Logo/T-Shirt/` เพื่อไม่ให้ทับกัน
สคริปต์ใน `source/` คัดลอกมาจาก `Team Logo/source/` ณ commit `efacb8d` แล้วแก้ต่อที่นี่ได้เลย
โลโก้ทีมยังอ่านจาก `Team Logo/svg/` ชุดเดิม

| โฟลเดอร์ | สร้างด้วย |
|---|---|
| `shirts/` | `python3 source/make_shirts.py shirts` · แบบรวม A / B / C |
| `team-front/` | `python3 source/make_team_fronts.py team-front` · หน้าแยกทีม T1 / T2 / T3 |
| `spec/` | `python3 source/make_print_spec.py spec` · แผ่นสเปกงานสกรีนแบบ A (cm) |
| `model/` | `python3 source/make_models.py model` · แบบ A บนหุ่นจำลอง |
| `design-a/` | `python3 source/make_design_a_v2.py design-a/svg` · **แบบ A v2**: ชื่อรายคน แผ่น A3 ต่อคน และ mockup พร้อมขนาด |
| `roster/` | `python3 source/make_roster.py roster.csv roster` · แผ่น A3 ของทุกคนใน `roster.csv` (SVG รายคน, PDF รวมแยกสีเสื้อ, `sizes.csv`) |
| `slides-deck/` | ต้นฉบับสไลด์ "TGR2026 Design A v2" |

แบบ A v2 (หน่วย mm ตามจริง): หลัง 26.0 × 30.0 cm · อกซ้าย 10.0 × 7.0 cm · แขนซ้าย 7.0 × 6.5 cm ทุกทีม
ลายสามจุดของหนึ่งคนวางรวมในกระดาษ A3 (29.7 × 42 cm) ได้ · แก้รายชื่อที่ `PEOPLE` ใน `make_design_a_v2.py`

รันจากโฟลเดอร์ `Team Logo/T-Shirt-v2/` (ต้องใช้ macOS และ `fonttools`)
