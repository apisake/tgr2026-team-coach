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
    # shirt-deck
    "d5d886365f864b683a0c5aee1cc0805b": "web/img/logo-canet.png",
    "799d52f6ed674571eeacf76706440648": "web/img/logo-click.png",
    "530c34dfb0041f122c173d1c198edc10": "web/img/logo-scroll.png",
    "01671555099b09ad6f134f2207d29fc7": "Team Logo/T-Shirt/png/shirt-A-white-front.png",
    "5484e14dc2252a44d3e5ec354a1ac68c": "Team Logo/T-Shirt/png/shirt-A-black-front.png",
    "63a83d2ac895bbabc8e6dacda87c3e81": "Team Logo/T-Shirt/png/shirt-B-white-front.png",
    "d28cc152e93bcdaf3e05e1b91b3afd01": "Team Logo/T-Shirt/png/shirt-B-black-front.png",
    "8e75a8cdcf6c0f92e3897256cdce44eb": "Team Logo/T-Shirt/png/shirt-C-white-front.png",
    "346c7c44654a4bcd11d2659ade6d4804": "Team Logo/T-Shirt/png/shirt-C-black-front.png",
    "0779c8dfa81e2e838b1f6a380e995c80": "Team Logo/T-Shirt/png/shirt-A-white-mockup.png",
    "dc20d4debf1adecd8738980f6079ed86": "Team Logo/T-Shirt/png/shirt-A-black-mockup.png",
    "90a3c05b0d4cfab822d04cf2ab053293": "Team Logo/T-Shirt/png/shirt-B-white-mockup.png",
    "e7c20944f0aad0f477b11c9cf709cdb6": "Team Logo/T-Shirt/png/shirt-B-black-mockup.png",
    "3e3a79a9e5c471c2cb6dfd2ef3348321": "Team Logo/T-Shirt/png/shirt-C-white-mockup.png",
    "9569e2cff60f77cb9b806344a6823876": "Team Logo/T-Shirt/png/shirt-C-black-mockup.png",
    # team-front-deck
    "1d51c6eef2383489b9d5d713df5de47b": "Team Logo/T-Shirt/team-front/png/team-T1-muzik.click-black.png",
    "36dc77cb74d191357b63a09436727136": "Team Logo/T-Shirt/team-front/png/team-T2-muzik.scroll-black.png",
    "fe9151e5980d88c4e6f8cf219d8a383c": "Team Logo/T-Shirt/team-front/png/team-T3-CANET-black.png",
    "5eae2e4f99bede99399c3f9433d03bfb": "Team Logo/T-Shirt/team-front/png/team-T1-CANET-white.png",
    "500ad84d027fc5ef2c900dda436de4a5": "Team Logo/T-Shirt/team-front/png/team-T2-muzik.click-white.png",
    "0dcdbadfff9f7d5da156c24ee203fd81": "Team Logo/T-Shirt/team-front/png/team-T3-muzik.scroll-white.png",
    "238f0691545d1680a061282ffabb6ee1": "Team Logo/T-Shirt/team-front/png/team-T1-white-lineup.png",
    "42924772c3b1b8f8d5774fc1ba9a189d": "Team Logo/T-Shirt/team-front/png/team-T1-black-lineup.png",
    "6dbd532d7ad30f84d5c11c3b17934142": "Team Logo/T-Shirt/team-front/png/team-T2-white-lineup.png",
    "a68f0d5bf57e16bdd0924311b2018342": "Team Logo/T-Shirt/team-front/png/team-T2-black-lineup.png",
    "e620b86b3f864b6d578a22f228c75bff": "Team Logo/T-Shirt/team-front/png/team-T3-white-lineup.png",
    "63221b9e5c1cce9d000d615f24fdeb83": "Team Logo/T-Shirt/team-front/png/team-T3-black-lineup.png",
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
