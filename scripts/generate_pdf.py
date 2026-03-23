"""
Phase 5: manuscript.md → PDF変換（weasyprint経由）
"""

import re
from pathlib import Path

import markdown
import weasyprint

PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_DIR / "output"
MANUSCRIPT_MD = PROJECT_DIR / "manuscript.md"

CSS = """
@page {
    size: A4;
    margin: 2.5cm 2cm;
    @bottom-center { content: counter(page); font-size: 10pt; color: #666; }
}
body {
    font-family: "Times New Roman", "DejaVu Serif", Georgia, serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #111;
}
h1 { font-size: 16pt; margin-top: 0; margin-bottom: 8pt; line-height: 1.3; }
h2 { font-size: 13pt; margin-top: 20pt; margin-bottom: 6pt; border-bottom: 1px solid #ccc; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; margin-top: 14pt; margin-bottom: 4pt; }
p { margin: 6pt 0; text-align: justify; }
blockquote { margin: 8pt 20pt; padding: 4pt 10pt; background: #f5f5f5; border-left: 3px solid #ccc; font-family: monospace; font-size: 9.5pt; }
table { border-collapse: collapse; width: 100%; margin: 10pt 0; font-size: 9.5pt; }
th, td { border: 1px solid #999; padding: 4pt 6pt; text-align: left; }
th { background: #e8e8e8; font-weight: bold; }
hr { border: none; border-top: 1px solid #ccc; margin: 16pt 0; }
img { max-width: 100%; height: auto; margin: 10pt 0; }
strong { font-weight: bold; }
"""


def convert():
    md_text = MANUSCRIPT_MD.read_text(encoding="utf-8")

    # Convert image paths to absolute file:// URIs
    md_text = re.sub(
        r'!\[([^\]]*)\]\((?!http)(.*?)\)',
        lambda m: f'![{m.group(1)}](file://{(PROJECT_DIR / m.group(2)).resolve()})',
        md_text,
    )

    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "smarty"],
    )

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{html_body}</body></html>"""

    out_path = OUTPUT_DIR / "manuscript.pdf"
    weasyprint.HTML(string=html, base_url=str(PROJECT_DIR)).write_pdf(str(out_path))
    print(f"[OK] {out_path}")


if __name__ == "__main__":
    convert()
