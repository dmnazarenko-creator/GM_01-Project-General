#!/usr/bin/env python3
"""Build branded PDF counterparts for every project Markdown document."""
from pathlib import Path
from html import escape
import re
import markdown
from PIL import Image
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Projects" / "GM_01-Project-General"
TARGET = SOURCE / "PDF"
TARGET.mkdir(parents=True, exist_ok=True)
LOGO = ROOT / "WAS_BlueWhite.png"

def brand_color():
    with Image.open(LOGO) as im:
        im = im.convert("RGB")
        im.thumbnail((320, 200))
        colors = im.getcolors(im.width * im.height) or []
    suitable = [(count, rgb) for count, rgb in colors
                if rgb[2] > rgb[0] * 1.15 and rgb[2] > rgb[1] * 1.05
                and max(rgb) < 210 and min(rgb) < 175]
    if suitable:
        r, g, b = max(suitable, key=lambda x:x[0])[1]
        return f"#{r:02x}{g:02x}{b:02x}"
    return "#17365d"  # Conservative fallback, check against WAS.pdf.

BLUE = brand_color()
CSS = """
@page { size: A4; margin: 28mm 18mm 20mm 18mm;
  @top-left { content: element(running-logo); }
  @bottom-left { content: "GM / Рабочая техническая документация"; font: 8pt 'DejaVu Sans'; color: #707984; }
  @bottom-right { content: "Стр. " counter(page) " / " counter(pages); font: 8pt 'DejaVu Sans'; color: #707984; }
}
body { font-family: 'DejaVu Sans', sans-serif; color: #202b35; font-size: 9.2pt; line-height: 1.5; }
#brand-header { position: running(running-logo); height: 19mm; }
#brand-header img { width: 38mm; max-height: 15mm; object-fit: contain; object-position: left center; }
h1 { color: BRAND; font-size: 19pt; border-bottom: 2px solid BRAND; padding-bottom: 6pt; }
h2 { color: BRAND; font-size: 13pt; border-bottom: .5px solid #bac5cf; padding-bottom: 4pt; margin-top: 18pt; }
h3 { color: BRAND; font-size: 11pt; }
h1, h2, h3 { break-after: avoid; }
p, li { overflow-wrap: anywhere; }
blockquote { border-left: 3px solid BRAND; padding: 5pt 10pt; margin: 10pt 0; background: #f3f6f8; }
table { border-collapse: collapse; width: 100%; font-size: 8pt; margin: 10pt 0; }
th, td { border: .5px solid #aebbc5; padding: 5pt 6pt; text-align: left; overflow-wrap: anywhere; }
th { background: BRAND; color: white; }
tr { break-inside: avoid; }
img { max-width: 100%; height: auto; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8pt; overflow-wrap: anywhere; }
pre { white-space: pre-wrap; background: #f4f6f8; padding: 8pt; }
a { color: BRAND; text-decoration: none; }
""".replace("BRAND", BLUE)

for path in sorted(SOURCE.glob("[0-9][0-9]-*.md")):
    md = path.read_text(encoding="utf-8")
    # The repository Markdown includes its own logo; PDF places it into the page header.
    md = "\n".join(line for line in md.split("\n") if not ('WAS_BlueWhite.png' in line and line.lstrip().startswith('<img ')))
    content = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
    document = (f'<!doctype html><html lang="ru"><head><meta charset="utf-8">'
                f'<title>{escape(path.stem)}</title><style>{CSS}</style></head>'
                f'<body><div id="brand-header"><img src="{LOGO.as_uri()}" alt="WAS"></div>'
                f'{content}</body></html>')
    output = TARGET / (path.stem + ".pdf")
    HTML(string=document, base_url=ROOT.as_uri()).write_pdf(output)
    print(f"Created {output.relative_to(ROOT)}: {output.stat().st_size} bytes")
