"""Compare ways to mark BAM (F) and BAM (M) on the back print: symbol after the name or after the role."""
import os, sys
from make_shirts import AVENIR, SHIRT, svg, text
from make_design_a_v2 import BACK, back_print, place

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

OPTIONS = [("sup", "A · SYMBOL AFTER NAME"), ("role", "B · SYMBOL AFTER ROLE")]
PEOPLE = [("female", "BAM (F)"), ("male", "BAM (M)")]

for color, mcol in [(c, m) for m in ("ink", "gender") for c in ("white", "black")]:
    W, H, pad, head = BACK[0], BACK[1], 16, 22
    cols = len(OPTIONS) * len(PEOPLE)
    total_w = cols * W + (cols + 1) * pad
    g = f'<rect width="{total_w}" height="{H + head + 2 * pad + 8}" fill="#E8ECEA"/>'
    i = 0
    for style, label in OPTIONS:
        for mark, who in PEOPLE:
            x = pad + i * (W + pad)
            g += text(AVENIR, f"{label} · {who}", x, pad + 8, 7, "#4E5D58", "start", 0.12)
            g += f'<rect x="{x}" y="{pad + head}" width="{W}" height="{H}" fill="{SHIRT[color]["fill"]}" stroke="#C9D1CD" stroke-width="0.5"/>'
            g += place(back_print(color, "BAM", "CREW", "CANET", mark=mark, mark_style=style, mark_color=mcol), x, pad + head)
            i += 1
    with open(os.path.join(OUT, f"mark-options-{color}{'-color' if mcol == 'gender' else ''}.svg"), "w") as fh:
        fh.write(svg(total_w, H + head + 2 * pad + 8, g, f"BAM gender mark options {color}"))
print("ok")
