"""Generate TGR2026 T-shirt mockups (front / back crew / back coach / sleeves) as SVG."""
import base64, os, sys
from fontTools.ttLib import TTCollection, TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_DIR = os.path.join(HERE, "..", "svg")

VIRIDIAN, CORAL, VIOLET = "#40826D", "#FF5A4F", "#7B5CFF"
VIRIDIAN_ON_DARK = "#5FB394"


def font(path, name=None):
    if name is None:
        return TTFont(path)
    for f in TTCollection(path).fonts:
        if f["name"].getDebugName(4) == name:
            return f
    raise KeyError(name)


FUTURA = font("/System/Library/Fonts/Supplemental/Futura.ttc", "Futura Bold")
MENLO = font("/System/Library/Fonts/Menlo.ttc", "Menlo Bold")
MENLO_R = font("/System/Library/Fonts/Menlo.ttc", "Menlo Regular")
AVENIR = font("/System/Library/Fonts/Avenir Next.ttc", "Avenir Next Demi Bold")
DIN = font("/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf")


def _draw(f, text, x, y, size, tracking):
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    scale = size / f["head"].unitsPerEm
    pen, cx = SVGPathPen(gs), 0.0
    for ch in text:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (scale, 0, 0, -scale, x + cx, y)))
        cx += gs[g].width * scale + tracking * size
    return pen.getCommands(), cx - tracking * size


def text(f, s, x, y, size, fill, anchor="start", tracking=0.0, opacity=1):
    _, w = _draw(f, s, 0, 0, size, tracking)
    x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
    d, _ = _draw(f, s, x0, y, size, tracking)
    op = f' fill-opacity="{opacity}"' if opacity != 1 else ""
    return f'<path d="{d}" fill="{fill}"{op}/>'


def width(f, s, size, tracking=0.0):
    return _draw(f, s, 0, 0, size, tracking)[1]


B64 = {k: base64.b64encode(open(os.path.join(LOGO_DIR, f"{k}-icon.svg"), "rb").read()).decode()
       for k in ("CANET", "muzik.click", "muzik.scroll")}
TEAMS = [("CANET", "CANET", VIRIDIAN), ("muzik.click", "muzik.click()", CORAL), ("muzik.scroll", "muzik.scroll()", VIOLET)]


def icon(key, cx, cy, size):
    return (f'<image href="data:image/svg+xml;base64,{B64[key]}" x="{cx - size / 2:.1f}" '
            f'y="{cy - size / 2:.1f}" width="{size}" height="{size}"/>')


SHIRT = {
    "white": dict(fill="#F6F6F3", edge="#D3D7D4", inner="#E2E5E2", ink="#14201C", sub="#5A6763", fold="#000000"),
    "black": dict(fill="#18191B", edge="#33373A", inner="#0C0D0E", ink="#F4F5F2", sub="#A9B4B0", fold="#FFFFFF"),
}


def team_color(c, color):
    return VIRIDIAN_ON_DARK if (c == VIRIDIAN and color == "black") else c


# ------------------------------------------------------------------ garments (600 x 660 panel)

def shirt(color, back=False):
    s = SHIRT[color]
    neck_q = 80 if back else 150
    body = (f"M200 50 Q300 {neck_q} 400 50 L505 85 L592 235 L520 278 L478 222 L482 628 "
            f"Q300 640 118 628 L122 222 L80 278 L8 235 L95 85 Z")
    return f"""
  <path d="{body}" fill="{s['fill']}" stroke="{s['edge']}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M200 50 Q300 {66 if back else 70} 400 50 Q300 {neck_q} 200 50 Z" fill="{s['inner']}"/>
  <path d="M200 50 Q300 {neck_q} 400 50" fill="none" stroke="{s['edge']}" stroke-width="13" stroke-linecap="round"/>
  <path d="M200 50 Q300 {neck_q} 400 50" fill="none" stroke="{s['fill']}" stroke-width="7" stroke-linecap="round" stroke-opacity="0.55"/>
  <path d="M584 241 L526 274 M16 241 L74 274" stroke="{s['edge']}" stroke-width="4"/>
  <path d="M122 610 Q300 622 478 610" fill="none" stroke="{s['edge']}" stroke-width="2.5"/>
  <path d="M160 300 Q170 420 150 560 M450 330 Q438 450 452 570 M122 222 Q130 240 126 260 M478 222 Q470 240 474 260"
        fill="none" stroke="{s['fold']}" stroke-opacity="0.05" stroke-width="10" stroke-linecap="round"/>
"""


def sleeve(color, oy):
    s = SHIRT[color]
    return f"""
  <path d="M150 {oy + 10} L450 {oy + 10} L478 {oy + 150} L122 {oy + 150} Z" fill="{s['fill']}" stroke="{s['edge']}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M126 {oy + 132} L474 {oy + 132}" stroke="{s['edge']}" stroke-width="3"/>
"""


# ------------------------------------------------------------------ print designs

def design_a(part, color, role=None, team=None, oy=0):
    """A · Badge Row — quiet left-chest badge, structured back."""
    s = SHIRT[color]
    if part == "front":
        g = "".join(icon(k, 352 + i * 38, 168, 34) for i, (k, _, _) in enumerate(TEAMS))
        g += text(AVENIR, "SILPAKORN UNIVERSITY", 390, 202, 9.5, s["ink"], "middle", 0.14)
        g += text(MENLO, "TGR2026", 390, 216, 9, s["sub"], "middle", 0.1)
        return g
    if part == "back":
        g = text(AVENIR, "SILPAKORN UNIVERSITY", 300, 128, 15, s["ink"], "middle", 0.22)
        rc = team_color(VIRIDIAN, color) if role == "COACH" else s["ink"]
        g += text(DIN, role, 300, 236, 96, rc, "middle", 0.04)
        for i, (k, name, c) in enumerate(TEAMS):
            cx = 196 + i * 104
            g += icon(k, cx, 296, 66)
            g += text(MENLO, name, cx, 348, 10.5, team_color(c, color), "middle")
        g += f'<path d="M190 380 H410" stroke="{s["sub"]}" stroke-width="1.5" stroke-opacity="0.6"/>'
        g += text(AVENIR, "TESA TOP GUN RALLY #20", 300, 408, 13, s["ink"], "middle", 0.16)
        g += text(AVENIR, "CHUMPHON · 15–21 NOV 2026", 300, 428, 11, s["sub"], "middle", 0.16)
        return g
    k, name, c = team
    return icon(k, 300, oy + 62, 54) + text(MENLO, name, 300, oy + 112, 15, team_color(c, color), "middle")


def design_b(part, color, role=None, team=None, oy=0):
    """B · Circuit Trace — logos as nodes on a PCB trace, code-block back."""
    s = SHIRT[color]
    trace = team_color(VIRIDIAN, color)
    if part == "front":
        g = text(AVENIR, "SILPAKORN UNIVERSITY", 300, 172, 15, s["ink"], "middle", 0.24)
        g += (f'<path d="M150 228 H452" stroke="{trace}" stroke-width="3"/>'
              f'<circle cx="146" cy="228" r="6" fill="none" stroke="{trace}" stroke-width="3"/>'
              f'<circle cx="456" cy="228" r="6" fill="none" stroke="{trace}" stroke-width="3"/>')
        for i, (k, _, _) in enumerate(TEAMS):
            cx = 204 + i * 96
            g += f'<circle cx="{cx}" cy="228" r="34" fill="{s["fill"]}"/>' + icon(k, cx, 226, 62)
        g += text(MENLO, "> TGR2026 · CHUMPHON", 300, 292, 12, s["sub"], "middle")
        return g
    if part == "back":
        kw, pun = (VIOLET if color == "white" else "#A894FF"), s["sub"]
        lines = [
            [("// TESA Top Gun Rally #20", pun)],
            [("const ", kw), ("silpakorn", s["ink"]), (" = {", pun)],
            [("  teams", s["ink"]), (": [", pun)],
            [('    "CANET"', team_color(VIRIDIAN, color)), (",", pun)],
            [('    "muzik.click()"', CORAL), (",", pun)],
            [('    "muzik.scroll()"', VIOLET if color == "white" else "#A894FF"), (",", pun)],
            [("  ],", pun)],
            [("  role", s["ink"]), (": ", pun), (f'"{role}"', team_color(VIRIDIAN, color) if role == "COACH" else CORAL), (",", pun)],
            [("};", pun)],
        ]
        g, y = "", 150
        for ln in lines:
            x = 168
            for t, col in ln:
                g += text(MENLO, t, x, y, 16, col)
                x += width(MENLO, t, 16)
            y += 30
        g += text(DIN, role, 300, 470, 64, s["ink"], "middle", 0.08, opacity=0.9)
        g += text(AVENIR, "SILPAKORN UNIVERSITY", 300, 500, 12, s["sub"], "middle", 0.24)
        return g
    k, name, c = team
    g = f'<path d="M190 {oy + 70} H410" stroke="{team_color(c, color)}" stroke-width="2.5"/>'
    g += f'<circle cx="300" cy="{oy + 70}" r="30" fill="{s["fill"]}"/>' + icon(k, 300, oy + 68, 52)
    g += text(MENLO, f"<{name}/>", 300, oy + 120, 14, team_color(c, color), "middle")
    return g


def design_c(part, color, role=None, team=None, oy=0):
    """C · Ganesha & Mushika — the story piece: elephant with two mice."""
    s = SHIRT[color]
    if part == "front":
        g = icon("CANET", 300, 200, 150)
        g += icon("muzik.click", 204, 258, 58) + icon("muzik.scroll", 396, 258, 58)
        g += text(FUTURA, "SILPAKORN", 300, 338, 30, s["ink"], "middle", 0.16)
        g += text(AVENIR, "UNIVERSITY", 300, 360, 12, s["sub"], "middle", 0.6)
        return g
    if part == "back":
        g = "".join(icon(k, 266 + i * 34, 112, 28) for i, (k, _, _) in enumerate(TEAMS))
        rc = team_color(VIRIDIAN, color) if role == "COACH" else s["ink"]
        g += text(FUTURA, role, 300, 240, 74, rc, "middle", 0.06)
        g += f'<path d="M200 268 H400" stroke="{rc}" stroke-width="3"/>'
        g += text(FUTURA, "CANET", 300, 310, 24, team_color(VIRIDIAN, color), "middle", 0.2)
        g += text(MENLO, "muzik.click()", 300, 336, 15, CORAL, "middle")
        g += text(MENLO, "muzik.scroll()", 300, 358, 15, VIOLET if color == "white" else "#A894FF", "middle")
        g += text(AVENIR, "SILPAKORN UNIVERSITY", 300, 410, 13, s["ink"], "middle", 0.22)
        g += text(AVENIR, "TESA TOP GUN RALLY #20 · TGR2026", 300, 430, 10, s["sub"], "middle", 0.16)
        return g
    k, name, c = team
    return icon(k, 300, oy + 64, 64) + text(FUTURA, name.upper().replace("()", ""), 300, oy + 116, 12, s["sub"], "middle", 0.3)


DESIGNS = {"A": design_a, "B": design_b, "C": design_c}

# ------------------------------------------------------------------ compose


def panel(inner, dx, label, s):
    return (f'<g transform="translate({dx} 20)">{inner}</g>'
            + text(AVENIR, label, dx + 300, 708, 18, "#4E5D58", "middle", 0.2))


def front_svg(d, color):
    s = SHIRT[color]
    return shirt(color) + DESIGNS[d]("front", color)


def back_svg(d, color, role):
    return shirt(color, back=True) + DESIGNS[d]("back", color, role=role)


def sleeves_svg(d, color):
    g = ""
    for i, t in enumerate(TEAMS):
        oy = 20 + i * 205
        g += sleeve(color, oy) + DESIGNS[d]("sleeve", color, team=t, oy=oy)
    return g


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<title>{title}</title>{body}</svg>\n')


if __name__ == "__main__":
    OUT = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    NAMES = {"A": "Badge Row", "B": "Circuit Trace", "C": "Ganesha and Mushika"}
    for d in DESIGNS:
        for color in ("white", "black"):
            s = SHIRT[color]
            bg = '<rect width="2400" height="740" fill="#E8ECEA"/>'
            body = (bg
                    + panel(front_svg(d, color), 0, "FRONT", s)
                    + panel(back_svg(d, color, "CREW"), 600, "BACK · CREW", s)
                    + panel(back_svg(d, color, "COACH"), 1200, "BACK · COACH", s)
                    + panel(sleeves_svg(d, color), 1800, "LEFT SLEEVE · BY TEAM", s))
            with open(os.path.join(OUT, f"shirt-{d}-{color}-mockup.svg"), "w") as fh:
                fh.write(svg(2400, 740, body, f"TGR2026 shirt {d} {NAMES[d]} {color}"))
            with open(os.path.join(OUT, f"shirt-{d}-{color}-front.svg"), "w") as fh:
                fh.write(svg(600, 680, f'<g transform="translate(0 10)">{front_svg(d, color)}</g>', f"TGR2026 shirt {d} front {color}"))
    print("ok", sorted(os.listdir(OUT)))
