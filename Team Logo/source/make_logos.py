"""Generate TGR2026 team logos as SVG (text outlined to paths)."""
import os, sys
from fontTools.ttLib import TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

VIRIDIAN = "#40826D"
VIRIDIAN_LIGHT = "#A8D5C2"
CORAL = "#FF5A4F"
CORAL_LIGHT = "#FFB3AD"
VIOLET = "#7B5CFF"
VIOLET_LIGHT = "#C9BDFF"
INK = "#14201C"
WHITE = "#FFFFFF"


def font(path, name):
    for f in TTCollection(path).fonts:
        if f["name"].getDebugName(4) == name:
            return f
    raise KeyError(name)


FUTURA_BOLD = font("/System/Library/Fonts/Supplemental/Futura.ttc", "Futura Bold")
MENLO_BOLD = font("/System/Library/Fonts/Menlo.ttc", "Menlo Bold")
AVENIR_DEMI = font("/System/Library/Fonts/Avenir Next.ttc", "Avenir Next Demi Bold")


def text_path(f, text, x, y, size, tracking=0.0):
    """Return (svg path d, advance width) for text with baseline at (x, y)."""
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    scale = size / f["head"].unitsPerEm
    pen = SVGPathPen(gs)
    cx = 0.0
    for ch in text:
        g = cmap[ord(ch)]
        tp = TransformPen(pen, (scale, 0, 0, -scale, x + cx, y))
        gs[g].draw(tp)
        cx += gs[g].width * scale + tracking * size
    return pen.getCommands(), cx - tracking * size


def text_width(f, text, size, tracking=0.0):
    return text_path(f, text, 0, 0, size, tracking)[1]


# ---------------------------------------------------------------- icons (512 box)

def canet_icon(c=VIRIDIAN, tusk=VIRIDIAN_LIGHT, uid="canet"):
    tusk_d = "M300 300 Q314 350 360 362"
    return f"""
  <defs>
    <mask id="{uid}-ears" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512">
      <rect width="512" height="512" fill="#fff"/>
      <circle cx="256" cy="206" r="114" fill="#000"/>
    </mask>
    <mask id="{uid}-head" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512">
      <rect width="512" height="512" fill="#fff"/>
      <circle cx="214" cy="200" r="11" fill="#000"/>
      <circle cx="298" cy="200" r="11" fill="#000"/>
      <rect x="244" y="128" width="24" height="24" transform="rotate(45 256 140)" fill="#000"/>
      <path d="{tusk_d}" stroke="#000" stroke-width="44" stroke-linecap="round" fill="none"/>
      <path d="M212 300 L204 318" stroke="#000" stroke-width="44" stroke-linecap="round" fill="none"/>
    </mask>
  </defs>
  <g mask="url(#{uid}-ears)" fill="{c}">
    <path d="M178 130 C112 112 70 160 76 222 C82 284 130 318 176 300 Z"/>
    <path d="M334 130 C400 112 442 160 436 222 C430 284 382 318 336 300 Z"/>
  </g>
  <g mask="url(#{uid}-head)">
    <circle cx="256" cy="206" r="98" fill="{c}"/>
    <path d="M284 250 V350 Q284 432 200 432 A20 20 0 0 1 200 392 Q228 392 228 344 V250 Z" fill="{c}"/>
  </g>
  <circle cx="152" cy="412" r="16" stroke="{c}" stroke-width="12" fill="none"/>
  <path d="{tusk_d}" stroke="{tusk}" stroke-width="22" stroke-linecap="round" fill="none"/>
  <path d="M212 300 L204 318" stroke="{tusk}" stroke-width="22" stroke-linecap="round" fill="none"/>
"""


MOUSE_BODY = '<rect x="176" y="150" width="160" height="270" rx="80"/>'


def muzik_icon(kind, c, light, uid):
    # shared: rat ears behind body, body, button seams, tail/cable
    seams = """
      <rect x="171" y="243" width="170" height="10" fill="#000"/>
      <rect x="251" y="140" width="10" height="108" fill="#000"/>"""
    if kind == "click":
        wheel = '<rect x="245" y="182" width="22" height="46" rx="11" fill="#000"/>'
        extra_mask = ""
        accents = f"""
  <path d="M176 248 V230 A80 80 0 0 1 251 150.2 V248 Z" fill="{light}" mask="url(#{uid}-body)"/>
  <g stroke="{c}" stroke-width="14" stroke-linecap="round">
    <path d="M132 226 L96 214"/>
    <path d="M138 268 L104 286"/>
    <path d="M140 186 L118 160"/>
  </g>"""
    else:
        wheel = '<rect x="239" y="170" width="34" height="70" rx="17" fill="#000"/>'
        extra_mask = ""
        accents = f"""
  <rect x="245" y="176" width="22" height="58" rx="11" fill="{light}"/>
  <g stroke="#000" stroke-width="0"/>
  <g stroke="{c}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <path d="M368 214 L392 190 L416 214"/>
    <path d="M368 316 L392 340 L416 316"/>
    <path d="M392 236 V294" stroke-dasharray="0.1 29"/>
  </g>"""
    return f"""
  <defs>
    <mask id="{uid}-ears" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512">
      <rect width="512" height="512" fill="#fff"/>
      <rect x="164" y="138" width="184" height="294" rx="92" fill="#000"/>
    </mask>
    <mask id="{uid}-body" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512">
      <rect width="512" height="512" fill="#fff"/>{seams}
      {wheel}{extra_mask}
    </mask>
  </defs>
  <g fill="{c}" mask="url(#{uid}-ears)">
    <circle cx="190" cy="146" r="46"/>
    <circle cx="322" cy="146" r="46"/>
  </g>
  <g fill="{c}" mask="url(#{uid}-body)">{MOUSE_BODY}</g>
  <path d="M256 432 C256 478 318 482 334 450 C348 422 392 424 404 452" stroke="{c}" stroke-width="13" stroke-linecap="round" fill="none"/>{accents}
"""


# ---------------------------------------------------------------- files

def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'  <title>{title}</title>{body}</svg>\n')


def write(name, content):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(content)


teams = [
    dict(slug="CANET", title="CANET", icon=lambda uid, c=VIRIDIAN: canet_icon(uid=uid),
         color=VIRIDIAN, word=[("CANET", VIRIDIAN, WHITE)], font=FUTURA_BOLD, tracking=0.12,
         tag="TGR2026 · MAIN TEAM"),
    dict(slug="muzik.click", title="muzik.click()",
         icon=lambda uid: muzik_icon("click", CORAL, CORAL_LIGHT, uid),
         color=CORAL, word=[("muzik", INK, WHITE), (".click()", CORAL, CORAL)], font=MENLO_BOLD, tracking=-0.02,
         tag="TGR2026 · OBSERVE TEAM"),
    dict(slug="muzik.scroll", title="muzik.scroll()",
         icon=lambda uid: muzik_icon("scroll", VIOLET, VIOLET_LIGHT, uid),
         color=VIOLET, word=[("muzik", INK, WHITE), (".scroll()", VIOLET, VIOLET)], font=MENLO_BOLD, tracking=-0.02,
         tag="TGR2026 · OBSERVE TEAM"),
]

for t in teams:
    s = t["slug"]
    write(f"{s}-icon.svg", svg(512, 512, t["icon"](f"{s.replace('.', '-')}-i"), t["title"]))

    # horizontal lockup: icon 300px tall + wordmark
    for mode in ("light", "dark"):
        size = 150
        x0, base = 330, 270
        parts, cx = [], x0
        for txt, col_light, col_dark in t["word"]:
            d, adv = text_path(t["font"], txt, cx, base, size, t["tracking"])
            parts.append(f'<path d="{d}" fill="{col_light if mode == "light" else col_dark}"/>')
            cx += adv + t["tracking"] * size
        tag_col = INK if mode == "light" else WHITE
        d, _ = text_path(AVENIR_DEMI, t["tag"], x0 + 4, base + 64, 34, 0.18)
        parts.append(f'<path d="{d}" fill="{tag_col}" fill-opacity="0.62"/>')
        width = int(cx + 40)
        icon = (f'<g transform="translate(10 25) scale(0.6)">'
                f'{t["icon"](s.replace(".", "-") + "-" + mode)}</g>')
        bg = '' if mode == "light" else f'<rect width="{width}" height="360" rx="40" fill="#0F1714"/>'
        write(f"{s}-lockup-{mode}.svg", svg(width, 360, bg + icon + "".join(parts), t["title"]))

    # stacked badge (square) for social / stickers
    for mode in ("light", "dark"):
        bg_col = "#FFFFFF" if mode == "light" else "#0F1714"
        size = 96 if t["slug"] == "CANET" else 78
        parts = []
        w = sum(text_width(t["font"], txt, size, t["tracking"]) + t["tracking"] * size for txt, *_ in t["word"]) - t["tracking"] * size
        cx = 512 - w / 2
        for txt, col_light, col_dark in t["word"]:
            d, adv = text_path(t["font"], txt, cx, 850, size, t["tracking"])
            parts.append(f'<path d="{d}" fill="{col_light if mode == "light" else col_dark}"/>')
            cx += adv + t["tracking"] * size
        tw = text_width(AVENIR_DEMI, t["tag"], 30, 0.18)
        d, _ = text_path(AVENIR_DEMI, t["tag"], 512 - tw / 2, 916, 30, 0.18)
        parts.append(f'<path d="{d}" fill="{INK if mode == "light" else WHITE}" fill-opacity="0.6"/>')
        body = (f'<rect width="1024" height="1024" rx="120" fill="{bg_col}"/>'
                f'<g transform="translate(232 120) scale(1.09375)">{t["icon"](s.replace(".", "-") + "-b" + mode)}</g>'
                + "".join(parts))
        write(f"{s}-badge-{mode}.svg", svg(1024, 1024, body, t["title"]))

print("ok", sorted(os.listdir(OUT)))
