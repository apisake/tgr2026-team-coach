# TGR2026 Team Coach

สื่อเตรียมทีมของภาควิชาคอมพิวเตอร์ คณะวิทยาศาสตร์ มหาวิทยาลัยศิลปากร สำหรับ TESA Top Gun Rally #20
หัวข้อ "แพลตฟอร์ม AIoT เพื่อขับเคลื่อนกาแฟโรบัสตาชุมพรสู่ตลาดยุคใหม่" · แข่ง 15–21 พ.ย. 2569 ที่ สจล. วิทยาเขตชุมพรเขตรอุดมศักดิ์

ทีม: **CANET** (ทีมหลัก · อ.อภิเษก หงษ์วิทยากร), **muzik.click()** (ผศ.ดร.สัจจาภรณ์ ไวจรรยา), **muzik.scroll()** (ผศ.ดร.ณัฐโชติ พรหมฤทธิ์)

## เนื้อหา

| ที่อยู่ | คืออะไร |
|---|---|
| `TGR2026-Coach-Plan.md` | วิเคราะห์โจทย์, component ที่ต้องเรียน, ความรู้ที่ต้องค้น, แผน 23 ต.ค.–21 พ.ย., โครงรายงานหลังแข่ง |
| `tutorial/` | บทเรียน Arduino + ESP32 บนบอร์ด IPST-WiFi (INEX) 10 บท สำหรับ C1 Embedded ตั้งแต่ติดตั้ง toolchain ถึงตัวควบคุมตู้อบที่ส่ง MQTT |
| `web/` | หน้าเว็บแผนเตรียมทีม (`plan.src.html` คือต้นฉบับ, `plan.html` คือไฟล์ที่ฝังโลโก้แล้ว) และภาพประกอบจาก proposal |
| `slides/plan-deck/` | ต้นฉบับสไลด์แผนเตรียมทีม 21 หน้า |
| `slides/shirt-deck/` | ต้นฉบับสไลด์แบบเสื้อ Crew/Coach 3 แบบ |
| `slides/team-front-deck/` | ต้นฉบับสไลด์เสื้อด้านหน้าแยกตามทีม 3 แนวคิด |
| `Team Logo/svg`, `Team Logo/png` | โลโก้ทั้งสามทีม (icon, lockup, badge · โหมดสว่าง/มืด) |
| `Team Logo/T-Shirt/` | mockup และไฟล์พิมพ์เสื้อแบบ A/B/C และ `team-front/` แบบ T1/T2/T3 |
| `Team Logo/source/` | สคริปต์ Python ที่สร้างโลโก้และเสื้อทั้งหมด |

## สร้างไฟล์ใหม่จากสคริปต์

ต้องใช้ macOS (ใช้ฟอนต์ Futura, Menlo, Avenir Next, DIN Condensed ของระบบ) และ `fonttools`

```bash
cd "Team Logo"
python3 source/make_logos.py svg
python3 source/make_shirts.py T-Shirt/svg
python3 source/make_team_fronts.py T-Shirt/team-front/svg
```

ไฟล์ PNG เรนเดอร์จาก SVG ด้วย Google Chrome แบบ headless

## หมายเหตุ

- ไฟล์ในโฟลเดอร์ `slides/` อ้างภาพผ่าน `/_blob/<id>` ซึ่งเป็นไฟล์ที่อัปโหลดไว้ใน deck บน claude.ai ภาพต้นฉบับเดียวกันอยู่ใน `web/img/` และ `Team Logo/`
- ภาพใน `web/img/fig*.jpg` นำมาจาก TGR2026 Proposal ของ TESA
- ตัวเลขด้านกาแฟในแผนเป็นค่าตั้งต้น ต้องตรวจกับแหล่งอ้างอิงก่อนใช้นำเสนอ
