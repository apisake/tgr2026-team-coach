"""Generate 1:1 Zoom profile pictures (1024 x 1024) for each team plus a shared one.

Full-square layout: university name on top, the logo as large as the square allows,
team name underneath.
"""
import os, sys
from make_shirts import AVENIR, FUTURA, MENLO, SHIRT, TEAMS, icon, svg, team_color, text, width

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

BG = {"light": "#F4F6F5", "dark": "#141618"}
SHIRT_MODE = {"light": "white", "dark": "black"}   # reuse the shirt ink/sub colours
C = 512


def header(mode):
    s = SHIRT[SHIRT_MODE[mode]]
    return (f'<rect width="1024" height="1024" fill="{BG[mode]}"/>'
            + text(AVENIR, "SILPAKORN UNIVERSITY", C, 118, 54, s["ink"], "middle", 0.12)
            + text(AVENIR, "TESA TOP GUN RALLY #20 · TGR2026", C, 168, 26, s["sub"], "middle", 0.2))


def fit(font, s, size, max_w, tracking=0.0):
    """Largest size up to `size` that keeps `s` within `max_w`."""
    w = width(font, s, size, tracking)
    return size if w <= max_w else size * max_w / w


def team_profile(key, name, c, mode):
    tc = team_color(c, SHIRT_MODE[mode])
    g = header(mode) + icon(key, C, 520, 640)
    if key == "CANET":
        g += text(FUTURA, name, C, 948, fit(FUTURA, name, 120, 880, 0.14), tc, "middle", 0.14)
    else:
        g += text(MENLO, name, C, 940, fit(MENLO, name, 110, 840), tc, "middle")
    return g


def all_teams(mode):
    s = SHIRT[SHIRT_MODE[mode]]
    g = (header(mode)
         + icon("muzik.click", 250, 690, 400)
         + icon("muzik.scroll", 774, 690, 400)
         + icon("CANET", C, 450, 500))
    x = C - sum(width(f, t, 40) for f, t, _ in [(FUTURA, "CANET", 0), (MENLO, "  muzik.click()  ", 0), (MENLO, "muzik.scroll()", 0)]) / 2
    for f, t, (k, _, c) in zip((FUTURA, MENLO, MENLO), ("CANET", "  muzik.click()  ", "muzik.scroll()"), TEAMS):
        g += text(f, t, x, 960, 40, team_color(c, SHIRT_MODE[mode]))
        x += width(f, t, 40)
    return g


for mode in BG:
    for key, name, c in TEAMS:
        with open(os.path.join(OUT, f"zoom-{key}-{mode}.svg"), "w") as fh:
            fh.write(svg(1024, 1024, team_profile(key, name, c, mode), f"{name} Zoom profile"))
    with open(os.path.join(OUT, f"zoom-all-teams-{mode}.svg"), "w") as fh:
        fh.write(svg(1024, 1024, all_teams(mode), "TGR2026 Silpakorn Zoom profile"))
print("ok", sorted(os.listdir(OUT)))
