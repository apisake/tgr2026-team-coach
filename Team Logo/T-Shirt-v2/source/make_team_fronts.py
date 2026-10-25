"""Generate per-team front designs (3 concepts x white/black) for the TGR2026 shirts."""
import math, os, sys
from make_shirts import (AVENIR, CORAL, FUTURA, MENLO, SHIRT, TEAMS, VIOLET, VIRIDIAN,
                         _draw, icon, shirt, svg, team_color, text, width)

def name_mark(key, name, x, y, color, c, canet_size=34, mono_size=24):
    """Team name in its own voice: CANET in Futura, muzik.*() in Menlo."""
    tc = team_color(c, color)
    if key == "CANET":
        return text(FUTURA, name, x, y, canet_size, tc, "middle", 0.16)
    return text(MENLO, name, x, y, mono_size, tc, "middle")


def hero(key, name, c, color):
    """T1 · Hero Mark — the team's own logo, big and centred."""
    s = SHIRT[color]
    g = icon(key, 300, 205, 170)
    g += name_mark(key, name, 300, 330, color, c)
    g += text(AVENIR, "SILPAKORN UNIVERSITY", 300, 360, 11, s["ink"], "middle", 0.3)
    g += text(MENLO, "TGR2026", 300, 377, 9, s["sub"], "middle", 0.2)
    return g


def wordmark(key, name, c, color):
    """T2 · Wordmark — the name carries the chest, the logo is the accent."""
    s = SHIRT[color]
    tc = team_color(c, color)
    g = icon(key, 300, 160, 64)
    if key == "CANET":
        g += text(FUTURA, "CANET", 300, 262, 76, tc, "middle", 0.08)
    else:
        g += text(MENLO, "muzik", 300, 252, 66, s["ink"], "middle")
        g += text(MENLO, name[5:], 300, 292, 34, tc, "middle")
    g += f'<path d="M190 316 H410" stroke="{tc}" stroke-width="3"/>'
    g += text(AVENIR, "SILPAKORN UNIVERSITY · TGR2026", 300, 340, 10.5, s["ink"], "middle", 0.24)
    return g


def arc_text(s, cx, cy, r, size, fill, bottom=False, tracking=0.28):
    """Glyphs set upright along an arc centred at 12 o'clock, or reading left to right along 6 o'clock."""
    widths = [width(AVENIR, ch, size) + tracking * size for ch in s]
    run = -sum(widths) / 2
    out = []
    for ch, w in zip(s, widths):
        mid = math.degrees((run + w / 2) / r)
        run += w
        if ch == " ":
            continue
        d, _ = _draw(AVENIR, ch, -(w - tracking * size) / 2, 0, size, 0)
        if bottom:
            out.append(f'<path d="{d}" fill="{fill}" transform="translate({cx} {cy}) rotate({-mid:.2f}) translate(0 {r})"/>')
        else:
            out.append(f'<path d="{d}" fill="{fill}" transform="translate({cx} {cy}) rotate({mid:.2f}) translate(0 {-r})"/>')
    return "".join(out)


def emblem(key, name, c, color):
    """T3 · Emblem — a round team seal with the university around the rim."""
    s = SHIRT[color]
    tc = team_color(c, color)
    cx, cy = 300, 228
    g = (f'<circle cx="{cx}" cy="{cy}" r="96" fill="none" stroke="{tc}" stroke-width="5"/>'
         f'<circle cx="{cx}" cy="{cy}" r="64" fill="none" stroke="{tc}" stroke-width="2"/>')
    g += arc_text("SILPAKORN UNIVERSITY", cx, cy, 74, 13, s["ink"])
    g += arc_text("TGR2026", cx, cy, 84, 13, s["ink"], bottom=True, tracking=0.5)
    g += (f'<circle cx="{cx - 79}" cy="{cy}" r="3" fill="{tc}"/>'
          f'<circle cx="{cx + 79}" cy="{cy}" r="3" fill="{tc}"/>')
    g += icon(key, cx, cy, 92)
    g += name_mark(key, name, 300, 370, color, c, canet_size=30, mono_size=21)
    return g


CONCEPTS = {"T1": hero, "T2": wordmark, "T3": emblem}

if __name__ == "__main__":
    OUT = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    for cid, fn in CONCEPTS.items():
        for color in ("white", "black"):
            body = '<rect width="1800" height="740" fill="#E8ECEA"/>'
            for i, (key, name, c) in enumerate(TEAMS):
                dx = i * 600
                panel = shirt(color) + fn(key, name, c, color)
                body += f'<g transform="translate({dx} 20)">{panel}</g>'
                body += text(MENLO if key != "CANET" else FUTURA, name, dx + 300, 708, 20,
                             "#4E5D58", "middle", 0.1 if key == "CANET" else 0)
                single = svg(600, 680, f'<g transform="translate(0 10)">{panel}</g>', f"TGR2026 {cid} {name} {color}")
                with open(os.path.join(OUT, f"team-{cid}-{key}-{color}.svg"), "w") as fh:
                    fh.write(single)
            with open(os.path.join(OUT, f"team-{cid}-{color}-lineup.svg"), "w") as fh:
                fh.write(svg(1800, 740, body, f"TGR2026 team fronts {cid} {color}"))
    print("ok", len(os.listdir(OUT)))
