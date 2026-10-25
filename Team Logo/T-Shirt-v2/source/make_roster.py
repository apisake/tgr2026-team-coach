"""A3 print sheets for everyone in roster.csv (design A v2), plus one A3 PDF per shirt colour.

Usage (from Team Logo/T-Shirt-v2):  python3 source/make_roster.py roster.csv roster
  roster/svg/a3-<id>-<colour>.svg   one A3 sheet per person and colour (for the print shop)
  roster/pdf/a3-<colour>.pdf        all sheets of that colour, one A3 page each
  roster/sizes.csv                  name, team, role, colour and the three print sizes
"""
import csv, os, subprocess, sys, tempfile
from make_design_a_v2 import BACK, FRONT, SLEEVE, a3_svg

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MARKS = {"M": "male", "F": "female"}   # optional roster column: gender symbol after the name
TEAM_KEYS = {"CANET": "CANET", "muzik.click()": "muzik.click", "muzik.click": "muzik.click",
             "muzik.scroll()": "muzik.scroll", "muzik.scroll": "muzik.scroll"}


def cm(box):
    return f"{box[0] / 10:.1f} x {box[1] / 10:.1f} cm"


def to_pdf(svg_paths, pdf_path):
    pages = "".join(f'<img src="file://{p}">' for p in svg_paths)
    html = ("<!doctype html><html><head><meta charset='utf-8'><style>"
            "@page{size:297mm 420mm;margin:0}html,body{margin:0}"
            "img{display:block;width:297mm;height:420mm;break-after:page}</style></head>"
            f"<body>{pages}</body></html>")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, dir=os.environ.get("TMPDIR")) as fh:
        fh.write(html)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--allow-file-access-from-files",
                    "--no-pdf-header-footer", f"--print-to-pdf={os.path.abspath(pdf_path)}", f"file://{fh.name}"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.unlink(fh.name)


def main(roster_csv, out):
    os.makedirs(os.path.join(out, "svg"), exist_ok=True)
    os.makedirs(os.path.join(out, "pdf"), exist_ok=True)
    by_color, rows = {}, []
    for r in csv.DictReader(open(roster_csv, encoding="utf-8")):
        name = r["name"].strip().upper()
        if len(name.replace(".", "")) > 5:
            raise SystemExit(f"{name}: more than 5 letters")
        key = TEAM_KEYS[r["team"].strip()]
        for color in r["colors"].split(";"):
            color = color.strip()
            path = os.path.abspath(os.path.join(out, "svg", f"a3-{r['id']}-{color}.svg"))
            with open(path, "w") as fh:
                fh.write(a3_svg(name, key, r["role"].strip(), color, tag=r["id"].upper(), mark=MARKS.get((r.get("mark") or "").strip().upper())))
            by_color.setdefault(color, []).append(path)
            rows.append([r["id"], name, r["team"], r["role"], color, cm(BACK), cm(FRONT), cm(SLEEVE)])
    for color, paths in by_color.items():
        to_pdf(paths, os.path.join(out, "pdf", f"a3-{color}.pdf"))
    with open(os.path.join(out, "sizes.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "name", "team", "role", "shirt", "back", "left chest", "left sleeve"])
        w.writerows(rows)
    print(f"{len(rows)} sheets ->", {c: len(p) for c, p in by_color.items()})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
