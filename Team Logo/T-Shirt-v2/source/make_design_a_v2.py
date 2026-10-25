"""Design A v2: personalised Badge Row, every print drawn at real size (1 SVG unit = 1 mm).

Each person's three prints (back with their name, left chest, left sleeve) fit on one A3
sheet (297 x 420 mm), so one transfer sheet covers one shirt.  Outputs per sample person:
  a3-<id>.svg        the A3 print sheet with dimensions
  mockup-<id>.svg    front / back / sleeve on the shirt with dimensions
"""
import os, sys
from make_shirts import (AVENIR, DIN, FUTURA, MENLO, SHIRT, TEAMS, VIRIDIAN, icon, shirt, svg,
                         team_color, text, width)

# print boxes (mm)
FRONT = (100, 70)
BACK = (260, 300)
SLEEVE = (70, 65)
A3 = (297, 420)

TEAM = {k: (k, n, c) for k, n, c in TEAMS}

# sample people: id, name (<= 5 letters), team key, role, shirt colour
PEOPLE = [
    ("tong", "TONG", "CANET", "CREW", "white"),
    ("ploy", "PLOY", "muzik.click", "CREW", "white"),
    ("bank", "BANK", "muzik.scroll", "CREW", "black"),
    ("arm", "ARM", "CANET", "COACH", "white"),
    ("arm-black", "ARM", "CANET", "COACH", "black"),
]


def ink(color):
    return SHIRT[color]["ink"], SHIRT[color]["sub"]


def fit(font, s, size, max_w, tracking=0.0):
    w = width(font, s, size, tracking)
    return size if w <= max_w else size * max_w / w


# ------------------------------------------------------------------ prints (mm, origin top-left)

def front_print(color):
    """Left chest, 100 x 70 mm: bigger logos, university on two lines."""
    a, sub = ink(color)
    g = "".join(icon(k, 18 + i * 32, 15, 28) for i, (k, _, _) in enumerate(TEAMS))
    g += text(AVENIR, "SILPAKORN", 50, 44, fit(AVENIR, "SILPAKORN", 12.5, 96, 0.14), a, "middle", 0.14)
    g += text(AVENIR, "UNIVERSITY", 50, 56, fit(AVENIR, "UNIVERSITY", 8.6, 96, 0.42), a, "middle", 0.42)
    g += text(MENLO, "TGR2026", 50, 67, 6.4, sub, "middle", 0.12)
    return g


def back_print(color, name, role, key):
    """Back, 260 x 300 mm: personal name as the hero, role, the three teams, the event."""
    a, sub = ink(color)
    role_c = team_color(VIRIDIAN, color) if role == "COACH" else a
    g = text(AVENIR, "SILPAKORN UNIVERSITY", 130, 14, fit(AVENIR, "SILPAKORN UNIVERSITY", 13, 240, 0.22), a, "middle", 0.22)
    g += text(DIN, name, 130, 112, fit(DIN, name, 120, 250, 0.03), a, "middle", 0.03)
    rw = width(DIN, role, 40, 0.18)
    g += (f'<path d="M40 142 H{130 - rw / 2 - 8:.1f} M{130 + rw / 2 + 8:.1f} 142 H220" stroke="{role_c}" stroke-width="1.6"/>'
          + text(DIN, role, 130, 156, 40, role_c, "middle", 0.18))
    for i, (k, n, c) in enumerate(TEAMS):
        cx = 50 + i * 80
        if k == key:   # the wearer's own team gets a ring
            g += f'<circle cx="{cx}" cy="203" r="35" fill="none" stroke="{team_color(c, color)}" stroke-width="1.8"/>'
        g += icon(k, cx, 203, 58)
        g += text(MENLO, n, cx, 252, fit(MENLO, n, 9.5, 68), team_color(c, color), "middle")
    g += f'<path d="M40 264 H220" stroke="{sub}" stroke-width="0.8"/>'
    g += text(AVENIR, "TESA TOP GUN RALLY #20", 130, 281, 11, a, "middle", 0.16)
    g += text(AVENIR, "CHUMPHON · 15–21 NOV 2026", 130, 295, 8.5, sub, "middle", 0.16)
    return g


def sleeve_print(color, key):
    """Left sleeve, 70 x 65 mm, identical footprint for every team."""
    _, name, c = TEAM[key]
    tc = team_color(c, color)
    g = icon(key, 35, 24, 46)
    if key == "CANET":
        g += text(FUTURA, name, 35, 60, fit(FUTURA, name, 13, 60, 0.12), tc, "middle", 0.12)
    else:
        g += text(MENLO, name, 35, 60, fit(MENLO, name, 13, 66), tc, "middle")
    return g


# ------------------------------------------------------------------ dimension helpers

def dim_h(x0, x1, y, label, col, size, t=None):
    t = t or size * 0.45
    return (f'<path d="M{x0} {y} H{x1} M{x0} {y - t} V{y + t} M{x1} {y - t} V{y + t}" stroke="{col}" '
            f'stroke-width="{size * 0.12:.2f}" fill="none"/>'
            + text(AVENIR, label, (x0 + x1) / 2, y - size * 0.45, size, col, "middle"))


def dim_v(y0, y1, x, label, col, size, side="right", t=None, rotate=False):
    t = t or size * 0.45
    g = (f'<path d="M{x} {y0} V{y1} M{x - t} {y0} H{x + t} M{x - t} {y1} H{x + t}" stroke="{col}" '
         f'stroke-width="{size * 0.12:.2f}" fill="none"/>')
    if rotate:   # label reads bottom-to-top just right of the line
        lx, ly = x + size * 1.15, (y0 + y1) / 2
        return g + f'<g transform="rotate(-90 {lx:.2f} {ly:.2f})">' + text(AVENIR, label, lx, ly, size, col, "middle") + '</g>'
    tx = x + size * 0.6 if side == "right" else x - size * 0.6
    return g + text(AVENIR, label, tx, (y0 + y1) / 2 + size * 0.35, size, col, "start" if side == "right" else "end")


def cm(mm):
    return f"{mm / 10:.1f} cm"


def place(inner, x, y, k=1.0):
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f})">{inner}</g>'


# ------------------------------------------------------------------ A3 sheet

def a3_sheet(name, key, role, color, tag=None):
    """A3 transfer sheet in mm; print areas tinted with the shirt colour."""
    s = SHIRT[color]
    line = "#3B4A44"
    g = f'<rect width="{A3[0]}" height="{A3[1]}" fill="#FFFFFF"/>'
    g += f'<rect x="1" y="1" width="{A3[0] - 2}" height="{A3[1] - 2}" fill="none" stroke="#9AA6A1" stroke-width="0.8" stroke-dasharray="4 3"/>'
    bx, by = (A3[0] - BACK[0]) / 2 - 6, 17
    fx, fy = bx, by + BACK[1] + 19
    sx, sy = fx + FRONT[0] + 22, fy
    for (x, y, (w, h)) in ((bx, by, BACK), (fx, fy, FRONT), (sx, sy, SLEEVE)):
        g += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{s["fill"]}" stroke="#C9D1CD" stroke-width="0.4"/>'
    g += place(back_print(color, name, role, key), bx, by)
    g += place(front_print(color), fx, fy)
    g += place(sleeve_print(color, key), sx, sy)
    # dimensions (cm labels, 6 mm type)
    g += dim_h(bx, bx + BACK[0], by - 6, cm(BACK[0]), line, 6)
    g += dim_v(by, by + BACK[1], bx + BACK[0] + 5, cm(BACK[1]), line, 6, rotate=True)
    g += dim_h(fx, fx + FRONT[0], fy - 6, cm(FRONT[0]), line, 6)
    g += dim_v(fy, fy + FRONT[1], fx + FRONT[0] + 5, cm(FRONT[1]), line, 6, rotate=True)
    g += dim_h(sx, sx + SLEEVE[0], sy - 6, cm(SLEEVE[0]), line, 6)
    g += dim_v(sy, sy + SLEEVE[1], sx + SLEEVE[0] + 5, cm(SLEEVE[1]), line, 6, rotate=True)
    labels = [("BACK", bx, by + BACK[1] + 5.5), ("LEFT CHEST", fx, fy + FRONT[1] + 5.5), ("LEFT SLEEVE", sx, sy + SLEEVE[1] + 5.5)]
    for lab, x, y in labels:
        g += text(AVENIR, lab, x, y, 4.5, "#6A7772", "start", 0.2)
    ix = sx + SLEEVE[0] + 16
    for i, line_txt in enumerate(["A3 SHEET", "29.7 × 42.0 cm", "", tag or name, TEAM[key][1], role, color.upper() + " SHIRT"]):
        f = MENLO if i >= 3 else AVENIR
        g += text(f, line_txt, ix, sy + 5 + i * 7.5, 4.6, "#14201C" if i in (0, 3) else "#6A7772")
    return g


# ------------------------------------------------------------------ shirt mockup with dimensions

PX_PER_MM = 356 / 520          # shirt panel: body 122..478 px = 52 cm (size L)
SLEEVE_PX_PER_MM = 380 / 200   # sleeve panel: opening 110..490 px = 20 cm
CARD = "#2B3034"


def front_panel(color):
    a, _ = ink(color)
    k = PX_PER_MM
    w, h = FRONT[0] * k, FRONT[1] * k
    x0, y0 = 395 - w / 2, 150
    g = shirt(color) + place(front_print(color), x0, y0, k)
    g += dim_h(x0, x0 + w, y0 - 8, cm(FRONT[0]), a, 11)
    g += dim_v(y0, y0 + h, x0 + w + 8, cm(FRONT[1]), a, 11)
    # enlarged detail for reading on screen
    dk = 2.4
    dx, dy = 300 - FRONT[0] * dk / 2, 360
    g += (f'<rect x="{dx - 10}" y="{dy - 10}" width="{FRONT[0] * dk + 20}" height="{FRONT[1] * dk + 20}" rx="12" '
          f'fill="{SHIRT[color]["fill"]}" stroke="{a}" stroke-width="1.3" stroke-dasharray="5 4"/>'
          + place(front_print(color), dx, dy, dk)
          + text(AVENIR, "DETAIL (ENLARGED)", 300, dy - 18, 10, SHIRT[color]["sub"], "middle", 0.25)
          + f'<path d="M{x0} {y0 + h + 2} L{dx + 30} {dy - 10}" stroke="{a}" stroke-width="1.1" stroke-dasharray="3 3"/>')
    return g


def back_panel(color, name, role, key):
    a, _ = ink(color)
    k = PX_PER_MM
    w, h = BACK[0] * k, BACK[1] * k
    neck = 80
    x0, y0 = 300 - w / 2, neck + 50 * k            # 5 cm below the neck seam
    g = shirt(color, back=True) + place(back_print(color, name, role, key), x0, y0, k)
    g += dim_h(x0, x0 + w, y0 - 10, cm(BACK[0]), a, 12)
    g += dim_v(y0, y0 + h, x0 + w + 10, cm(BACK[1]), a, 12)
    g += (f'<path d="M{x0 - 12} {neck} V{y0}" stroke="{a}" stroke-width="1.3" stroke-dasharray="4 3"/>'
          + text(AVENIR, "5 cm", x0 - 18, (neck + y0) / 2 + 4, 11, a, "end"))
    return g


def sleeve_panel(color, key):
    s = SHIRT[color]
    a, _ = ink(color)
    k = SLEEVE_PX_PER_MM
    w, h = SLEEVE[0] * k, SLEEVE[1] * k
    hem = 446
    x0, y0 = 300 - w / 2, hem - 40 * k - h        # 4 cm above the hem
    g = (f'<path d="M150 150 L450 150 L490 470 L110 470 Z" fill="{s["fill"]}" stroke="{s["edge"]}" '
         f'stroke-width="3" stroke-linejoin="round"/>'
         f'<path d="M114 {hem} L486 {hem}" stroke="{s["edge"]}" stroke-width="3"/>')
    g += place(sleeve_print(color, key), x0, y0, k)
    g += dim_h(x0, x0 + w, y0 - 12, cm(SLEEVE[0]), a, 15)
    g += dim_v(y0, y0 + h, x0 + w + 12, cm(SLEEVE[1]), a, 15)
    g += (f'<path d="M{x0 - 18} {y0 + h} V{hem}" stroke="{a}" stroke-width="1.4" stroke-dasharray="4 3"/>'
          + text(AVENIR, "4 cm", x0 - 24, (y0 + h + hem) / 2 + 5, 14, a, "end"))
    g += text(AVENIR, "SHOULDER", 300, 136, 13, "#9AA6A1", "middle", 0.3)
    g += text(AVENIR, "SLEEVE HEM", 300, 500, 13, "#9AA6A1", "middle", 0.3)
    return g


def card(inner, dx):
    return (f'<rect x="{dx + 10}" y="0" width="580" height="700" rx="28" fill="{CARD}"/>'
            f'<g transform="translate({dx} 30)">{inner}</g>')


def a3_svg(name, key, role, color, tag=None):
    return svg(A3[0], A3[1], a3_sheet(name, key, role, color, tag), f"A3 sheet {name} {key} {role} {color}")


def mockup_svg(name, key, role, color):
    body = (card(front_panel(color), 0) + card(back_panel(color, name, role, key), 600)
            + card(sleeve_panel(color, key), 1200))
    return svg(1800, 700, body, f"Design A v2 {name} {key} {role} {color}")


if __name__ == "__main__":
    OUT = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    for pid, name, key, role, color in PEOPLE:
        with open(os.path.join(OUT, f"a3-{pid}.svg"), "w") as fh:
            fh.write(a3_svg(name, key, role, color))
        with open(os.path.join(OUT, f"mockup-{pid}.svg"), "w") as fh:
            fh.write(mockup_svg(name, key, role, color))
    print("ok", sorted(os.listdir(OUT)))
