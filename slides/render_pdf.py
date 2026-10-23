"""Render a slide deck folder (deck.json + slides/*.html) to a 1920x1080 PDF.

Usage: python3 slides/render_pdf.py slides/plan-deck slides/plan-deck.pdf
"""
import json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Uploaded deck assets -> the same images kept in this repo.
BLOBS = {
    "8045d524fbdd1240295239358c69acb1": "web/img/fig1a-robusta.jpg",
    "a14bf925894d76e2ce09b8d9c402f362": "web/img/fig1b-harvest.jpg",
    "907e0091c10431c965621fab285517dc": "web/img/fig2-pain-points.jpg",
    "d61f83c73df45d0cc6851a1cc3ac8f4f": "web/img/fig3-tech-gaps.jpg",
    "abbf8f54629796151d844ec6a30be383": "web/img/fig4-system-diagram.jpg",
    "d90476729dc46f56a66b2442fa9ca8c8": "web/img/logo-canet.png",
    "3ac4ca2fe31cf4284d3896c7ce8a63ad": "web/img/logo-click.png",
    "03b3d9a259aadee9a0e0122a77cfe5be": "web/img/logo-scroll.png",
}

ICONS = {
    "CheckCircle": '<circle cx="12" cy="12" r="10"/><path d="M7.5 12.5l3 3 6-6.5"/>',
    "Check": '<path d="M5 12.5l4.5 4.5L19 7"/>',
}

CSS = """
@page { size: 1920px 1080px; margin: 0 }
html, body { margin: 0; padding: 0 }
section { width: 1920px; height: 1080px; box-sizing: border-box; position: relative; overflow: hidden;
          page-break-after: always; break-after: page }
section * { margin: 0; box-sizing: border-box }
h1 { font-size: 96px; font-weight: 600; line-height: 1.1 }
h2 { font-size: 64px; font-weight: 600; line-height: 1.15 }
h3 { font-size: 44px; font-weight: 600; line-height: 1.2 }
p, li { line-height: 1.4 }
ul, ol { padding-left: 1.3em }
table { border-collapse: collapse; width: 100% }
th, td { padding: 0.35em 0.6em; text-align: left; vertical-align: top; border-bottom: 1px solid rgba(128,128,128,.35) }
th { font-weight: 600 }
aside { display: none }
x-icon { display: inline-block; flex: none }
x-icon svg { width: 100%; height: 100% }
"""


def icon_svg(m):
    attrs = m.group(1)
    name = re.search(r'name="([^"]+)"', attrs).group(1)
    style = re.search(r'style="([^"]*)"', attrs)
    body = ICONS.get(name, ICONS["Check"])
    svg = (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
           f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>')
    return f'<x-icon style="{style.group(1) if style else ""}">{svg}</x-icon>'


def main(deck_dir, out_pdf):
    deck = json.load(open(os.path.join(deck_dir, "deck.json")))
    hrefs = [f["href"] for f in deck.get("faces", {}).values() if "href" in f]
    parts = []
    for sid in deck["order"]:
        html = open(os.path.join(deck_dir, "slides", f"{sid}.html")).read()
        html = re.sub(r"/_blob/([0-9a-f]{32})",
                      lambda m: "file://" + os.path.join(ROOT, BLOBS[m.group(1)]), html)
        html = re.sub(r"<x-icon([^>]*)></x-icon>", icon_svg, html)
        parts.append(html)
    links = "".join(f'<link rel="stylesheet" href="{h}">' for h in hrefs)
    doc = (f'<!doctype html><html><head><meta charset="utf-8"><title>{deck["title"]}</title>{links}'
           f"<style>{CSS}</style></head><body>{''.join(parts)}</body></html>")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, dir=os.environ.get("TMPDIR")) as fh:
        fh.write(doc)
        tmp = fh.name
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--allow-file-access-from-files",
                    "--no-pdf-header-footer", "--virtual-time-budget=15000",
                    f"--print-to-pdf={os.path.abspath(out_pdf)}", f"file://{tmp}"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.unlink(tmp)
    print("wrote", out_pdf, len(deck["order"]), "slides")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
