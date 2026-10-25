"""Print-spec sheets for design A (Badge Row): front, back and left sleeve with sizes in cm.

Prints are scaled to realistic sizes for a size-L shirt (chest 52 cm flat) and annotated
with dimension lines, like a print shop's placement sheet. Thai labels live on the slides.
"""
import os, sys
from make_shirts import (AVENIR, DIN, MENLO, SHIRT, TEAMS, VIRIDIAN, design_a, shirt, svg,
                         team_color, text, width)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

CM_PER_PX = 52 / 356            # shirt panel: body 122..478 px = 52 cm chest (size L)
SLEEVE_CM_PER_PX = 20 / 380     # sleeve panel: opening 110..490 px = 20 cm
TARGET_CM = {"front": 9.0, "back": 28.0, "sleeve": 7.0}
CARD = "#2B3034"
INK = {"white": "#14201C", "black": "#F4F5F2"}


def front_bbox():
    w = max(width(AVENIR, "SILPAKORN UNIVERSITY", 9.5, 0.14), 3 * 38 - 4)
    return (390 - w / 2, 151, 390 + w / 2, 218)


def back_bbox(role):
    widths = [width(AVENIR, "SILPAKORN UNIVERSITY", 15, 0.22), width(DIN, role, 96, 0.04),
              width(AVENIR, "TESA TOP GUN RALLY #20", 13, 0.16),
              width(AVENIR, "CHUMPHON · 15–21 NOV 2026", 11, 0.16)]
    left = min(300 - max(widths) / 2, 196 - max(33, width(MENLO, "CANET", 10.5) / 2))
    right = max(300 + max(widths) / 2, 404 + width(MENLO, "muzik.scroll()", 10.5) / 2)
    return (left, 117, right, 431)


def sleeve_bbox(team, oy):
    _, name, _ = team
    w = max(54, width(MENLO, name, 15))
    return (300 - w / 2, oy + 35, 300 + w / 2, oy + 116)


def scaled(inner, box, target_px, anchor=None, s=None):
    """Scale artwork so its bbox is target_px wide (or by `s`), keeping `anchor` (default bbox centre) fixed."""
    x0, y0, x1, y1 = box
    s = s or target_px / (x1 - x0)
    ax, ay = anchor or ((x0 + x1) / 2, (y0 + y1) / 2)
    new = (ax + (x0 - ax) * s, ay + (y0 - ay) * s, ax + (x1 - ax) * s, ay + (y1 - ay) * s)
    return f'<g transform="translate({ax} {ay}) scale({s:.4f}) translate({-ax} {-ay})">{inner}</g>', new


def dims(box, cm_w, cm_h, ink, gap=10, size=13, label_gap=6):
    """Width line above the print and height line to its right, with end ticks and cm labels."""
    x0, y0, x1, y1 = box
    ty, rx = y0 - gap, x1 + gap
    t = 5
    g = (f'<g stroke="{ink}" stroke-width="1.6" fill="none">'
         f'<path d="M{x0} {ty} H{x1} M{x0} {ty - t} V{ty + t} M{x1} {ty - t} V{ty + t}"/>'
         f'<path d="M{rx} {y0} V{y1} M{rx - t} {y0} H{rx + t} M{rx - t} {y1} H{rx + t}"/></g>')
    g += text(AVENIR, f"{cm_w:.1f} cm", (x0 + x1) / 2, ty - label_gap, size, ink, "middle")
    g += text(AVENIR, f"{cm_h:.1f} cm", rx + 8, (y0 + y1) / 2 + size / 3, size, ink)
    return g


def gap_line(x, y_from, y_to, cm, ink, size=12):
    g = (f'<path d="M{x} {y_from} V{y_to}" stroke="{ink}" stroke-width="1.4" stroke-dasharray="4 3"/>'
         f'<path d="M{x - 5} {y_from} H{x + 5} M{x - 5} {y_to} H{x + 5}" stroke="{ink}" stroke-width="1.4"/>')
    return g + text(AVENIR, f"{cm:.0f} cm", x - 8, (y_from + y_to) / 2 + size / 3, size, ink, "end")


SIZES = {}


def front_panel(color):
    box = front_bbox()
    art, b = scaled(design_a("front", color), box, TARGET_CM["front"] / CM_PER_PX)
    w_cm, h_cm = (b[2] - b[0]) * CM_PER_PX, (b[3] - b[1]) * CM_PER_PX
    SIZES["front"] = (w_cm, h_cm)
    # enlarged detail so the badge can be read on screen
    ix0, iy0, ix1, iy1 = 170, 400, 430, 540
    detail, _ = scaled(design_a("front", color), box, 0, s=220 / (box[2] - box[0]))
    dx, dy = (ix0 + ix1) / 2 - (box[0] + box[2]) / 2, (iy0 + iy1) / 2 - (box[1] + box[3]) / 2
    inset = (f'<rect x="{ix0}" y="{iy0}" width="{ix1 - ix0}" height="{iy1 - iy0}" rx="14" fill="{SHIRT[color]["fill"]}" '
             f'stroke="{INK[color]}" stroke-width="1.4" stroke-dasharray="5 4"/>'
             f'<g transform="translate({dx:.1f} {dy:.1f})">{detail}</g>'
             + text(AVENIR, "DETAIL (ENLARGED)", (ix0 + ix1) / 2 - 30, iy0 - 10, 10, SHIRT[color]["sub"], "middle", 0.25)
             + f'<path d="M{b[0]} {b[3] + 4} L{ix1 - 40} {iy0}" stroke="{INK[color]}" stroke-width="1.2" stroke-dasharray="3 3"/>')
    return shirt(color) + art + dims(b, w_cm, h_cm, INK[color], size=12) + inset


def back_panel(color, role):
    box = back_bbox(role)
    neck_y = 80                                   # back neckline seam (shirt panel coords)
    top_y = neck_y + 5 / CM_PER_PX                # print starts 5 cm below the neck seam
    art, b = scaled(design_a("back", color, role=role), box, TARGET_CM["back"] / CM_PER_PX,
                    anchor=(300, box[1]))
    dy = top_y - b[1]
    art = f'<g transform="translate(0 {dy:.1f})">{art}</g>'
    b = (b[0], b[1] + dy, b[2], b[3] + dy)
    w_cm, h_cm = (b[2] - b[0]) * CM_PER_PX, (b[3] - b[1]) * CM_PER_PX
    SIZES[f"back-{role}"] = (w_cm, h_cm)
    return (shirt(color, back=True) + art + dims(b, w_cm, h_cm, INK[color], gap=14)
            + gap_line(b[0] - 14, neck_y, b[1], 5, INK[color]))


def sleeve_panel(color, team):
    s = SHIRT[color]
    key, name, c = team
    shape = (f'<path d="M150 210 L450 210 L490 470 L110 470 Z" fill="{s["fill"]}" stroke="{s["edge"]}" '
             f'stroke-width="3" stroke-linejoin="round"/>'
             f'<path d="M114 446 L486 446" stroke="{s["edge"]}" stroke-width="3"/>')
    oy = 250
    box = sleeve_bbox(team, oy)
    ref = sleeve_bbox(TEAMS[2], oy)               # the widest sleeve print sets one scale for all teams
    k = TARGET_CM["sleeve"] / SLEEVE_CM_PER_PX / (ref[2] - ref[0])
    art, b = scaled(design_a("sleeve", color, team=team, oy=oy), box, 0, s=k)
    w_cm, h_cm = (b[2] - b[0]) * SLEEVE_CM_PER_PX, (b[3] - b[1]) * SLEEVE_CM_PER_PX
    SIZES[f"sleeve-{key}"] = (w_cm, h_cm)
    hem_gap = (446 - b[3]) * SLEEVE_CM_PER_PX
    return (shape + art + dims(b, w_cm, h_cm, INK[color], gap=16, size=15)
            + gap_line(b[0] - 26, b[3], 446, hem_gap, INK[color], size=14)
            + text(AVENIR, "SHOULDER", 300, 196, 13, "#9AA6A1", "middle", 0.3)
            + text(AVENIR, "SLEEVE HEM", 300, 500, 13, "#9AA6A1", "middle", 0.3))


def card(inner, dx, scale=1.0):
    return (f'<rect x="{dx + 10}" y="0" width="580" height="700" rx="28" fill="{CARD}"/>'
            f'<g transform="translate({dx + 300 - 300 * scale} {30}) scale({scale})">{inner}</g>')


for color in ("white", "black"):
    for team in TEAMS:
        body = (card(front_panel(color), 0) + card(back_panel(color, "CREW"), 600)
                + card(sleeve_panel(color, team), 1200))
        with open(os.path.join(OUT, f"spec-A-{team[0]}-{color}.svg"), "w") as fh:
            fh.write(svg(1800, 700, body, f"Design A print spec {team[1]} {color}"))
body = card(back_panel("white", "COACH"), 0) + card(back_panel("black", "COACH"), 600)
with open(os.path.join(OUT, "spec-A-coach.svg"), "w") as fh:
    fh.write(svg(1200, 700, body, "Design A print spec coach"))
for k, (w, h) in SIZES.items():
    print(f"{k}: {w:.1f} x {h:.1f} cm")
