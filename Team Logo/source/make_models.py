"""Design A (Badge Row) on an illustrated model: front, back and left-sleeve views per team.

Outputs 1920x1080 SVG scenes, one per team x shirt colour, plus coach backs and sleeve line-ups.
"""
import os, sys
from make_shirts import AVENIR, MENLO, SHIRT, TEAMS, design_a, icon, shirt, svg, team_color, text

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

SKIN, SKIN_SHADE = "#D9A27E", "#C48C69"
HAIR = "#2B2522"
PANTS, PANTS_SEAM = "#3B4A5C", "#2F3C4B"
SHOES = "#22262A"
BG = "#E8ECEA"
LABEL = "#4E5D58"


def legs_front():
    return (f'<path d="M205 560 L395 560 L388 930 L310 930 L300 640 L290 930 L212 930 Z" fill="{PANTS}"/>'
            f'<path d="M300 600 L300 640" stroke="{PANTS_SEAM}" stroke-width="3"/>'
            f'<ellipse cx="250" cy="944" rx="46" ry="16" fill="{SHOES}"/>'
            f'<ellipse cx="350" cy="944" rx="46" ry="16" fill="{SHOES}"/>')


def arms_front():
    g = ""
    for sx in (1, -1):
        x = lambda v: v if sx == 1 else 600 - v
        g += (f'<path d="M{x(142)} 322 Q{x(128)} 480 {x(140)} 640" stroke="{SKIN}" stroke-width="46" '
              f'stroke-linecap="round" fill="none"/>'
              f'<circle cx="{x(140)}" cy="652" r="25" fill="{SKIN}"/>')
    return g


def neck():
    return f'<rect x="278" y="158" width="44" height="54" rx="12" fill="{SKIN_SHADE}"/>'


def head_front():
    return (f'<ellipse cx="250" cy="118" rx="9" ry="13" fill="{SKIN_SHADE}"/>'
            f'<ellipse cx="350" cy="118" rx="9" ry="13" fill="{SKIN_SHADE}"/>'
            f'<ellipse cx="300" cy="112" rx="50" ry="60" fill="{SKIN}"/>'
            f'<path d="M249 108 Q248 44 300 42 Q352 44 351 108 Q342 70 300 72 Q258 70 249 108 Z" fill="{HAIR}"/>')


def head_back():
    return (f'<ellipse cx="250" cy="118" rx="9" ry="13" fill="{SKIN_SHADE}"/>'
            f'<ellipse cx="350" cy="118" rx="9" ry="13" fill="{SKIN_SHADE}"/>'
            f'<ellipse cx="300" cy="112" rx="50" ry="60" fill="{SKIN}"/>'
            f'<path d="M248 112 Q246 42 300 42 Q354 42 352 112 Q350 150 330 160 L270 160 Q250 150 248 112 Z" fill="{HAIR}"/>')


def on_body(inner):
    """Shirt artwork (600x660 panel) scaled onto the figure's torso."""
    return f'<g transform="translate(114 169) scale(0.62)">{inner}</g>'


def front_view(color):
    return legs_front() + arms_front() + neck() + on_body(shirt(color) + design_a("front", color)) + head_front()


def back_view(color, role):
    return (legs_front() + arms_front() + neck()
            + on_body(shirt(color, back=True) + design_a("back", color, role=role)) + head_back())


def side_view(color, team):
    """Person seen from their left side, facing the viewer's left: the left sleeve faces us."""
    s = SHIRT[color]
    key, name, c = team
    g = (f'<path d="M254 560 L346 560 L338 930 L264 930 Z" fill="{PANTS}"/>'
         f'<ellipse cx="284" cy="944" rx="60" ry="16" fill="{SHOES}"/>')
    g += (f'<path d="M258 204 Q300 194 342 204 L354 300 Q360 440 352 572 L248 572 Q240 440 246 300 Z" '
          f'fill="{s["fill"]}" stroke="{s["edge"]}" stroke-width="2.5" stroke-linejoin="round"/>'
          f'<path d="M250 556 Q300 562 350 556" fill="none" stroke="{s["edge"]}" stroke-width="2"/>')
    g += f'<rect x="278" y="158" width="38" height="52" rx="12" fill="{SKIN_SHADE}"/>'
    g += (f'<ellipse cx="296" cy="112" rx="48" ry="60" fill="{SKIN}"/>'
          f'<path d="M250 102 Q240 116 249 124 Q252 127 250 132" fill="{SKIN}" stroke="{SKIN_SHADE}" stroke-width="2"/>'
          f'<path d="M254 90 Q262 44 312 48 Q350 56 346 112 Q344 150 330 164 Q320 132 314 110 Q292 94 254 90 Z" fill="{HAIR}"/>'
          f'<ellipse cx="312" cy="122" rx="8" ry="12" fill="{SKIN_SHADE}"/>')
    g += (f'<path d="M300 300 Q298 480 294 640" stroke="{SKIN}" stroke-width="44" stroke-linecap="round" fill="none"/>'
          f'<circle cx="294" cy="654" r="24" fill="{SKIN}"/>')
    g += (f'<path d="M262 210 Q300 200 338 210 L348 332 L252 332 Z" fill="{s["fill"]}" '
          f'stroke="{s["edge"]}" stroke-width="2.5" stroke-linejoin="round"/>'
          f'<path d="M253 320 L347 320" stroke="{s["edge"]}" stroke-width="2.5"/>')
    g += icon(key, 300, 256, 54)
    g += text(MENLO, name, 300, 302, 9.5, team_color(c, color), "middle")
    return g


def scene(views, labels, title):
    """Three 600x1000 figures across a 1920x1080 canvas, captioned underneath."""
    body = f'<rect width="1920" height="1080" fill="{BG}"/>'
    for i, (v, lab) in enumerate(zip(views, labels)):
        x = 60 + i * 600
        body += f'<g transform="translate({x} 28)">{v}</g>'
        body += text(AVENIR, lab, x + 300, 1040, 24, LABEL, "middle", 0.2)
    return svg(1920, 1080, body, title)


def write(name, content):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(content)


for color in ("white", "black"):
    for team in TEAMS:
        key, name, _ = team
        write(f"model-A-{key}-{color}.svg",
              scene([front_view(color), back_view(color, "CREW"), side_view(color, team)],
                    ["FRONT", "BACK · CREW", f"LEFT SLEEVE · {name.upper()}"],
                    f"Design A on model {name} {color}"))
    write(f"model-A-sleeves-{color}.svg",
          scene([side_view(color, t) for t in TEAMS], [t[1].upper() for t in TEAMS],
                f"Design A sleeves by team {color}"))
write("model-A-coach.svg",
      scene([back_view("white", "COACH"), front_view("black"), back_view("black", "COACH")],
            ["WHITE · BACK · COACH", "BLACK · FRONT", "BLACK · BACK · COACH"], "Design A coach"))
print("ok", len(os.listdir(OUT)))
