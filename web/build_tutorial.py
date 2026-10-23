"""สร้าง web/tutorial.html จากไฟล์ใน tutorial/ (README.md ของแต่ละบท + สเก็ตช์ .ino/.h)

    python web/build_tutorial.py

แก้เนื้อหาที่ไฟล์ใน tutorial/ แล้วรันสคริปต์นี้ใหม่ ไม่ต้องแก้ tutorial.html เอง
ไม่ต้องติดตั้งไลบรารีเพิ่ม (มีตัวแปลง Markdown แบบย่อในไฟล์นี้)
"""

import html
import posixpath
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TUT = ROOT / "tutorial"
OUT = ROOT / "web" / "tutorial.html"
REPO = "https://github.com/apisake/tgr2026-team-coach/tree/main/tutorial"

# (id, ไฟล์ markdown, โฟลเดอร์สเก็ตช์, ป้ายสั้นในแถบนำทาง)
LESSONS = [
    ("setup", "00-setup.md", "L00_board_check", "ติดตั้ง"),
    ("L01_gpio", "L01_gpio/README.md", "L01_gpio", "GPIO"),
    ("L02_pwm_buzzer", "L02_pwm_buzzer/README.md", "L02_pwm_buzzer", "PWM"),
    ("L03_adc", "L03_adc/README.md", "L03_adc", "ADC"),
    ("L04_oled", "L04_oled/README.md", "L04_oled", "OLED"),
    ("L05_zx_sensors", "L05_zx_sensors/README.md", "L05_zx_sensors", "ZX sensors"),
    ("L06_i2c_sensor", "L06_i2c_sensor/README.md", "L06_i2c_sensor", "I2C"),
    ("L07_wifi_ntp", "L07_wifi_ntp/README.md", "L07_wifi_ntp", "Wi-Fi + NTP"),
    ("L08_mqtt_json", "L08_mqtt_json/README.md", "L08_mqtt_json", "MQTT"),
    ("L09_drying_controller", "L09_drying_controller/README.md", "L09_drying_controller", "ตู้อบ"),
]

# ---------------------------------------------------------------------------
# ลิงก์ระหว่างไฟล์ → anchor ในหน้าเดียว
# ---------------------------------------------------------------------------

def resolve_link(href, md_path):
    if re.match(r"^[a-z]+:", href) or href.startswith("#"):
        return href
    base = posixpath.dirname(md_path)
    path = posixpath.normpath(posixpath.join(base, href))
    if path == "README.md":
        return "#overview"
    if path == "../TGR2026-Coach-Plan.md":
        return "plan.html"
    for lid, md, sketch, _ in LESSONS:
        if path == md:
            return f"#{lid}"
        if path.startswith(sketch + "/"):
            return f"#code-{lid}"
    return f"{REPO}/{path}"

# ---------------------------------------------------------------------------
# Markdown แบบย่อ: หัวข้อ, ย่อหน้า, รายการ (ซ้อนได้), ตาราง, code fence, blockquote
# ---------------------------------------------------------------------------

def inline(text, md_path):
    codes = []

    def keep_code(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = text.replace("\\*", "\x01")
    links = []

    def keep_link(label, href):
        href = resolve_link(href, md_path)
        ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        links.append((label, href, ext))
        return f"\x02{len(links) - 1}\x02"

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: keep_link(m.group(1), m.group(2)), text)
    text = re.sub(r"<(https?://[^>]+)>", lambda m: keep_link(m.group(1), m.group(1)), text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    def put_link(m):
        label, href, ext = links[int(m.group(1))]
        return f'<a href="{html.escape(href)}"{ext}>{inline(label, md_path)}</a>'

    text = re.sub(r"\x02(\d+)\x02", put_link, text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)
    return text.replace("\x01", "*")


LIST_RE = re.compile(r"^(\s*)(-|\d+\.)\s+(.*)$")


def render_table(rows, md_path):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    head, body = cells[0], cells[2:]
    out = ['<div class="tbl"><table><thead><tr>']
    out += [f"<th>{inline(c, md_path)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join(f"<td>{inline(c, md_path)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def render_code(code, lang):
    label = {"bash": "shell", "cpp": "C++", "json": "JSON"}.get(lang, lang)
    tag = f'<span class="lang">{html.escape(label)}</span>' if label else ""
    body = highlight_cpp(code) if lang == "cpp" else html.escape(code)
    return (f'<div class="snip">{tag}<button class="copy" type="button">คัดลอก</button>'
            f"<pre><code>{body}</code></pre></div>")


def render_blocks(lines, md_path, tight=False):
    out = []
    i = 0
    para = []

    def flush():
        if para:
            text = inline(" ".join(s.strip() for s in para), md_path)
            out.append(text if tight and not out else f"<p>{text}</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            flush(); i += 1; continue
        if s.startswith("```"):
            flush()
            lang = s[3:].strip()
            indent = len(line) - len(line.lstrip())
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i][indent:] if lines[i][:indent].strip() == "" else lines[i])
                i += 1
            i += 1
            if not lang and code and code[0].lstrip().startswith("{"):
                lang = "json"
            out.append(render_code("\n".join(code), lang))
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            flush()
            level = len(m.group(1)) + 1  # # → h2 ในหน้าเว็บ
            out.append(f"<h{level}>{inline(m.group(2), md_path)}</h{level}>")
            i += 1; continue
        if s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i]); i += 1
            out.append(render_table(rows, md_path))
            continue
        if s.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            out.append(f'<div class="note">{render_blocks(quote, md_path, tight=True)}</div>')
            continue
        m = LIST_RE.match(line)
        if m and len(m.group(1)) == len(line) - len(line.lstrip()):
            flush()
            base = len(m.group(1))
            ordered = m.group(2) != "-"
            items = []
            while i < len(lines):
                m2 = LIST_RE.match(lines[i])
                if m2 and len(m2.group(1)) == base and (m2.group(2) != "-") == ordered:
                    items.append([m2.group(3)])
                    cont = base + len(m2.group(2)) + 1
                    i += 1
                    while i < len(lines):
                        l = lines[i]
                        if not l.strip():
                            nxt = next((x for x in lines[i + 1:] if x.strip()), "")
                            if len(nxt) - len(nxt.lstrip()) > base:
                                items[-1].append(""); i += 1; continue
                            break
                        ind = len(l) - len(l.lstrip())
                        if ind > base:
                            items[-1].append(l[min(ind, cont):]); i += 1
                        else:
                            break
                else:
                    break
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{render_blocks(it, md_path, tight=True)}</li>" for it in items) + f"</{tag}>")
            continue
        para.append(line)
        i += 1
    flush()
    return "\n".join(out)

# ---------------------------------------------------------------------------
# ไฮไลต์ C++ แบบง่าย (comment, string, preprocessor, keyword, ตัวเลข)
# ---------------------------------------------------------------------------

CPP_KW = set("""bool break case char const constexpr continue default do double else enum false float
for if int long return short signed sizeof static struct switch true uint8_t uint16_t uint32_t
unsigned void while size_t nullptr String auto byte""".split())
CPP_TOKEN = re.compile(r'(//[^\n]*)|("(?:\\.|[^"\\])*")|(\'(?:\\.|[^\'\\])\')|(^\s*#\w+[^\n]*)|(\b\d+(?:\.\d+)?[fUL]*\b|\b0x[0-9A-Fa-f]+\b)|(\b[A-Za-z_]\w*\b)', re.M)


def highlight_cpp(code):
    out, pos = [], 0
    for m in CPP_TOKEN.finditer(code):
        out.append(html.escape(code[pos:m.start()]))
        tok = html.escape(m.group(0))
        if m.group(1): out.append(f'<span class="c">{tok}</span>')
        elif m.group(2) or m.group(3): out.append(f'<span class="s">{tok}</span>')
        elif m.group(4): out.append(f'<span class="p">{tok}</span>')
        elif m.group(5): out.append(f'<span class="n">{tok}</span>')
        elif m.group(6) in CPP_KW: out.append(f'<span class="k">{tok}</span>')
        else: out.append(tok)
        pos = m.end()
    out.append(html.escape(code[pos:]))
    return "".join(out)

# ---------------------------------------------------------------------------
# ประกอบหน้า
# ---------------------------------------------------------------------------

def sketch_panel(lid, sketch):
    folder = TUT / sketch
    files = sorted(folder.glob("*.ino")) + sorted(folder.glob("*.h"))
    tabs = []
    for f in files:
        code = f.read_text(encoding="utf-8").rstrip("\n")
        n = code.count("\n") + 1
        tabs.append(
            f'<details class="sketch" open><summary><span class="fn">{f.name}</span>'
            f'<span class="ln">{n} บรรทัด</span></summary>'
            f'<div class="bar"><button class="copy" type="button">คัดลอก</button>'
            f'<button class="dl" type="button" data-name="{f.name}">ดาวน์โหลด</button>'
            f'<a href="{REPO}/{sketch}" target="_blank" rel="noopener">GitHub</a></div>'
            f'<pre><code>{highlight_cpp(code)}</code></pre></details>')
    return f'<div class="code" id="code-{lid}"><h3>โค้ด · <code>{sketch}</code></h3>{"".join(tabs)}</div>'


def split_title(md_text):
    lines = md_text.splitlines()
    title = lines[0].lstrip("# ").strip()
    return title, lines[1:]


def build():
    overview_title, overview_lines = split_title((TUT / "README.md").read_text(encoding="utf-8"))
    overview = render_blocks(overview_lines, "README.md")

    sections, nav = [], ['<a href="#overview"><span>·</span>ภาพรวม</a>']
    for n, (lid, md, sketch, short) in enumerate(LESSONS):
        title, body = split_title((TUT / md).read_text(encoding="utf-8"))
        title = re.sub(r"^บทที่ \d+ · ", "", title)
        nav.append(f'<a href="#{lid}" data-lesson="{lid}"><span>{n}</span>{html.escape(short)}</a>')
        sections.append(
            f'<section id="{lid}" data-lesson="{lid}">'
            f'<h2><span class="n">{n}</span><span class="t">{inline(title, md)}</span>'
            f'<label class="done"><input type="checkbox" data-done="{lid}"> เรียนแล้ว</label></h2>'
            f"{render_blocks(body, md)}{sketch_panel(lid, sketch)}</section>")

    page = TEMPLATE
    for key, val in {
        "{{TITLE}}": inline(overview_title, "README.md").replace("<code>", "").replace("</code>", ""),
        "{{NAV}}": "\n    ".join(nav),
        "{{OVERVIEW}}": overview,
        "{{SECTIONS}}": "\n\n".join(sections),
    }.items():
        page = page.replace(key, val)
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page.encode()):,} bytes)")


TEMPLATE = r"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>IPST-WiFi Arduino Tutorial</title>
<meta name="description" content="บทเรียน Arduino + ESP32 บนบอร์ด IPST-WiFi สำหรับทีม TGR2026">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@500;600;700&family=IBM+Plex+Sans+Thai:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap">
<style>
/* สไตล์เดียวกับ plan.html: คอลัมน์อ่านเดียว, แถบบทเรียน sticky, โค้ดพับได้ */
:root {
  --bg: #F6F8F7; --surface: #FFFFFF; --fg: #16201D; --muted: #5A6763; --line: #DCE3E0;
  --viridian: #40826D; --viridian-ink: #2F6655; --viridian-soft: #E3EFEA;
  --warn-soft: #FFF4D6; --warn-ink: #7A5600;
  --code-bg: #F0F4F2; --c-comment: #6B7A75; --c-string: #A23B72; --c-kw: #2F6655; --c-num: #9A5B00; --c-pp: #6A4BF0;
  --f-display: "Bai Jamjuree", "Sukhumvit Set", "Thonburi", system-ui, sans-serif;
  --f-body: "IBM Plex Sans Thai", "Sukhumvit Set", "Thonburi", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0F1714; --surface: #16211D; --fg: #E6EEEA; --muted: #9DAEA8; --line: #2A3833;
  --viridian: #5FA88C; --viridian-ink: #8CCBB2; --viridian-soft: #1C2E27;
  --warn-soft: #3A3018; --warn-ink: #F2D27A;
  --code-bg: #111B17; --c-comment: #7F928B; --c-string: #F08DBE; --c-kw: #8CCBB2; --c-num: #F2B66B; --c-pp: #A996FF;
  color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #0F1714; --surface: #16211D; --fg: #E6EEEA; --muted: #9DAEA8; --line: #2A3833;
  --viridian: #5FA88C; --viridian-ink: #8CCBB2; --viridian-soft: #1C2E27;
  --warn-soft: #3A3018; --warn-ink: #F2D27A;
  --code-bg: #111B17; --c-comment: #7F928B; --c-string: #F08DBE; --c-kw: #8CCBB2; --c-num: #F2B66B; --c-pp: #A996FF;
  color-scheme: dark }

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--fg); font: 400 16px/1.7 var(--f-body); }
.wrap { max-width: 920px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
a { color: var(--viridian-ink); }
:focus-visible { outline: 2px solid var(--viridian); outline-offset: 2px; }

header.top { background: var(--surface); border-bottom: 1px solid var(--line); }
header.top .wrap { padding-block: 40px 28px; display: grid; gap: 14px; }
.eyebrow { font: 600 12px/1 var(--f-mono); letter-spacing: .12em; text-transform: uppercase; color: var(--viridian-ink); }
h1 { font: 700 clamp(26px, 5vw, 40px)/1.25 var(--f-display); margin: 0; text-wrap: balance; }
.meta { display: flex; flex-wrap: wrap; gap: 8px 24px; font-size: 14px; color: var(--muted); }
.meta b { color: var(--fg); font-weight: 600; }
.progress { display: flex; align-items: center; gap: 12px; font-size: 14px; color: var(--muted); }
.progress .bar { flex: 1; max-width: 280px; height: 6px; border-radius: 3px; background: var(--viridian-soft); overflow: hidden; }
.progress .bar i { display: block; height: 100%; width: 0; background: var(--viridian); transition: width .3s; }

nav.toc { position: sticky; top: 0; z-index: 5; background: color-mix(in srgb, var(--surface) 92%, transparent); backdrop-filter: blur(8px); border-bottom: 1px solid var(--line); }
nav.toc .wrap { display: flex; gap: 4px; overflow-x: auto; padding-block: 8px; scrollbar-width: none; }
nav.toc a { flex: none; text-decoration: none; color: var(--muted); font-size: 14px; padding: 6px 10px; border-radius: 8px; white-space: nowrap; }
nav.toc a:hover, nav.toc a.here { background: var(--viridian-soft); color: var(--viridian-ink); }
nav.toc a span { font-family: var(--f-mono); color: var(--viridian); margin-right: 6px; }
nav.toc a.done span::after { content: "✓"; margin-left: 2px; }

main .wrap { padding-block: 8px 64px; }
section { padding-top: 44px; scroll-margin-top: 56px; }
section + section { border-top: 1px solid var(--line); margin-top: 32px; }
h2 { font: 700 26px/1.3 var(--f-display); margin: 0 0 16px; display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: baseline; text-wrap: balance; }
h2 .n { font: 600 15px/1 var(--f-mono); color: var(--viridian); border: 1.5px solid var(--viridian); border-radius: 6px; padding: 5px 7px; }
h2 .t { flex: 1 1 300px; }
h2 code { font-size: .8em; }
.done { font: 500 14px/1 var(--f-body); color: var(--muted); display: inline-flex; gap: 6px; align-items: center; cursor: pointer; white-space: nowrap; }
.done input { accent-color: var(--viridian); width: 16px; height: 16px; }
h3 { font: 600 19px/1.4 var(--f-display); margin: 28px 0 10px; }
h4 { font: 600 16px/1.4 var(--f-display); margin: 20px 0 8px; }
p { margin: 0 0 12px; max-width: 70ch; }
ul, ol { margin: 0 0 12px; padding-left: 22px; max-width: 72ch; }
li { margin: 4px 0; }
li > .snip, li > .tbl { margin-top: 8px; }
strong { font-weight: 600; }
code { font: 400 .88em var(--f-mono); background: var(--viridian-soft); padding: 1px 5px; border-radius: 4px; overflow-wrap: anywhere; }

.note { background: var(--warn-soft); color: var(--warn-ink); border-radius: 10px; padding: 12px 16px; font-size: 15px; margin: 14px 0; max-width: 72ch; }
.note code { background: color-mix(in srgb, var(--warn-ink) 12%, transparent); }

.tbl { overflow-x: auto; margin: 10px 0 18px; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); }
table { border-collapse: collapse; width: 100%; font-size: 15px; line-height: 1.55; }
th, td { text-align: left; vertical-align: top; padding: 9px 14px; border-bottom: 1px solid var(--line); }
tr:last-child td { border-bottom: 0; }
th { font: 600 12px/1.4 var(--f-mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); background: var(--bg); }
@media (min-width: 700px) { td code { white-space: nowrap; } }

pre { margin: 0; padding: 14px 16px; overflow-x: auto; font: 400 13.5px/1.6 var(--f-mono); tab-size: 2; }
pre code { background: none; padding: 0; font-size: inherit; overflow-wrap: normal; }
.snip { position: relative; background: var(--code-bg); border: 1px solid var(--line); border-radius: 10px; margin: 10px 0 16px; max-width: 100%; }
.snip .lang { position: absolute; top: 8px; left: 14px; font: 600 11px/1 var(--f-mono); color: var(--muted); text-transform: uppercase; letter-spacing: .08em; }
.snip .lang + .copy + pre { padding-top: 28px; }
.snip .copy { position: absolute; top: 6px; right: 6px; }
button { font: 500 13px/1 var(--f-body); color: var(--viridian-ink); background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 6px 10px; cursor: pointer; }
button:hover { background: var(--viridian-soft); }

.code { margin-top: 28px; }
details.sketch { background: var(--code-bg); border: 1px solid var(--line); border-radius: 10px; margin: 10px 0; }
details.sketch summary { display: flex; gap: 12px; align-items: baseline; padding: 10px 14px; cursor: pointer; font-family: var(--f-mono); }
details.sketch summary .fn { font-weight: 600; }
details.sketch summary .ln { color: var(--muted); font-size: 13px; }
details.sketch .bar { display: flex; gap: 6px; align-items: center; padding: 0 14px 8px; border-bottom: 1px solid var(--line); flex-wrap: wrap; }
details.sketch .bar a { font-size: 13px; margin-left: auto; }
details.sketch pre { max-height: 640px; }
.c { color: var(--c-comment); } .s { color: var(--c-string); } .k { color: var(--c-kw); font-weight: 600; } .n { color: var(--c-num); } .p { color: var(--c-pp); }

footer { border-top: 1px solid var(--line); color: var(--muted); font-size: 13px; }
footer .wrap { padding-block: 20px 40px; }
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="eyebrow">TGR2026 · C1 Embedded · ESP32 + Sensor</div>
    <h1>{{TITLE}}</h1>
    <div class="meta">
      <span><b>บอร์ด</b> INEX IPST-WiFi (TTGO T8 · ESP32)</span>
      <span><b>เครื่องมือ</b> Arduino IDE 2 · ESP32 core 3.3.x</span>
      <span><b>เป้าหมาย</b> ต่อเซ็นเซอร์ใหม่ + ส่ง MQTT ใน 30 นาที</span>
    </div>
    <div class="progress"><span id="prog-text">เรียนแล้ว 0 / 10 บท</span><div class="bar"><i id="prog-bar"></i></div></div>
  </div>
</header>

<nav class="toc" aria-label="บทเรียน">
  <div class="wrap">
    {{NAV}}
  </div>
</nav>

<main><div class="wrap">

<section id="overview">
{{OVERVIEW}}
</section>

{{SECTIONS}}

</div></main>

<footer><div class="wrap">สร้างจากโฟลเดอร์ <code>tutorial/</code> ด้วย <code>web/build_tutorial.py</code> · ภาควิชาคอมพิวเตอร์ คณะวิทยาศาสตร์ มหาวิทยาลัยศิลปากร · ทีม CANET, muzik.click(), muzik.scroll()</div></footer>

<script>
// คัดลอก / ดาวน์โหลดโค้ด
document.addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  const pre = btn.closest(".snip, details")?.querySelector("pre");
  if (!pre) return;
  const text = pre.textContent;
  if (btn.classList.contains("copy")) {
    navigator.clipboard.writeText(text).then(() => {
      const old = btn.textContent; btn.textContent = "คัดลอกแล้ว";
      setTimeout(() => (btn.textContent = old), 1200);
    });
  } else if (btn.classList.contains("dl")) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text + "\n"], { type: "text/plain" }));
    a.download = btn.dataset.name;
    a.click();
    URL.revokeObjectURL(a.href);
  }
});

// ติ๊ก "เรียนแล้ว" เก็บในเบราว์เซอร์ของแต่ละคน
const KEY = "ipst-tutorial-done";
let done = {};
try { done = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (_) {}
const boxes = [...document.querySelectorAll("input[data-done]")];
function refresh() {
  const n = boxes.filter((b) => b.checked).length;
  document.getElementById("prog-text").textContent = `เรียนแล้ว ${n} / ${boxes.length} บท`;
  document.getElementById("prog-bar").style.width = `${(100 * n) / boxes.length}%`;
  boxes.forEach((b) => document.querySelector(`nav a[data-lesson="${b.dataset.done}"]`)?.classList.toggle("done", b.checked));
}
boxes.forEach((b) => {
  b.checked = !!done[b.dataset.done];
  b.addEventListener("change", () => {
    done[b.dataset.done] = b.checked;
    try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (_) {}
    refresh();
  });
});
refresh();

// ไฮไลต์บทที่กำลังอ่านในแถบนำทาง
const links = new Map([...document.querySelectorAll("nav.toc a")].map((a) => [a.getAttribute("href").slice(1), a]));
const io = new IntersectionObserver((entries) => {
  entries.forEach((en) => {
    if (!en.isIntersecting) return;
    links.forEach((a) => a.classList.remove("here"));
    const a = links.get(en.target.id);
    if (a) { a.classList.add("here"); a.scrollIntoView({ block: "nearest", inline: "nearest" }); }
  });
}, { rootMargin: "-30% 0px -65% 0px" });
document.querySelectorAll("main section").forEach((s) => io.observe(s));
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
