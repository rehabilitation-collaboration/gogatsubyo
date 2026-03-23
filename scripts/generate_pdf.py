"""
Phase 5: manuscript.md -> PDF (weasyprint)
Figures (PNG) and Tables (CSV) are embedded after the main text.
"""

import csv
import re
from pathlib import Path

import markdown
import weasyprint

PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_DIR / "output"
MANUSCRIPT_MD = PROJECT_DIR / "manuscript.md"

FIGURE_FILES = {
    "Figure 1": "figure1_monthly_rate.png",
    "Figure 2": "figure2_forest_plot.png",
    "Figure 3": "figure3_era_comparison.png",
}

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
h2 { font-size: 13pt; margin-top: 20pt; margin-bottom: 6pt;
     border-bottom: 1px solid #ccc; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; margin-top: 14pt; margin-bottom: 4pt; }
p { margin: 6pt 0; text-align: justify; }
blockquote {
    margin: 8pt 20pt; padding: 4pt 10pt;
    background: #f5f5f5; border-left: 3px solid #ccc;
    font-family: monospace; font-size: 9.5pt;
}
table {
    border-collapse: collapse; width: 100%; margin: 10pt 0;
    font-size: 9pt;
}
th, td {
    border: 1px solid #999; padding: 3pt 5pt; text-align: left;
}
th { background: #e8e8e8; font-weight: bold; }
td.num { text-align: right; }
hr { border: none; border-top: 1px solid #ccc; margin: 16pt 0; }
img { max-width: 100%; height: auto; margin: 10pt 0; }
strong { font-weight: bold; }
.figure-block {
    page-break-inside: avoid;
    margin: 1.5em 0;
    text-align: center;
}
.figure-block img {
    display: block;
    margin: 0 auto;
    max-width: 95%;
}
.figure-caption {
    font-size: 10pt;
    text-align: justify;
    margin-top: 0.5em;
}
.table-block {
    page-break-inside: avoid;
    margin: 1.5em 0;
}
.table-caption {
    font-size: 10pt;
    margin-bottom: 0.5em;
    text-align: justify;
}
"""


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fmt(val: str, decimals: int = 3, is_pvalue: bool = False) -> str:
    """Format numeric string to fixed decimals, pass through non-numeric."""
    try:
        v = float(val)
        if is_pvalue:
            if v < 0.001:
                return "<0.001"
            return f"{v:.{decimals}f}"
        if v == 0.0 or abs(v) >= 1000:
            return f"{v:,.0f}"
        if abs(v) < 0.001:
            return "<0.001"
        return f"{v:.{decimals}f}"
    except (ValueError, TypeError):
        return val


def build_table1(rows: list[dict]) -> str:
    """Table 1: Descriptive statistics by age group."""
    all_rows = [r for r in rows if r["age_group"] == "all"]
    age_labels = {
        "under_20": "<20", "20-29": "20-29", "30-39": "30-39",
        "40-49": "40-49", "50-59": "50-59", "60-69": "60-69",
        "70-79": "70-79", "80_over": "80+",
    }
    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    html = '<div class="table-block">'
    html += '<p class="table-caption"><strong>Table 1.</strong> '
    html += "Descriptive statistics of monthly suicide counts by age group "
    html += "in Japan (2009-2024). Values are mean (SD) of monthly counts "
    html += "and rates per 100,000 person-years across 16 years.</p>"
    html += "<table><thead><tr>"
    html += "<th>Month</th><th>All ages<br>Count</th><th>Rate</th>"
    for label in age_labels.values():
        html += f"<th>{label}<br>Rate</th>"
    html += "</tr></thead><tbody>"

    for i, m_name in enumerate(month_names, 1):
        m_str = str(i)
        a = next((r for r in all_rows if r["month"] == m_str), None)
        html += "<tr>"
        bold = ' style="font-weight:bold"' if m_name == "May" else ""
        html += f"<td{bold}>{m_name}</td>"
        if a:
            html += f'<td class="num">{fmt(a["mean_count"], 1)} ({fmt(a["sd_count"], 1)})</td>'
            html += f'<td class="num">{fmt(a["mean_rate"], 1)}</td>'
        else:
            html += "<td>-</td><td>-</td>"
        for ag in age_labels:
            r = next(
                (x for x in rows if x["age_group"] == ag and x["month"] == m_str),
                None,
            )
            if r:
                html += f'<td class="num">{fmt(r["mean_rate"], 1)}</td>'
            else:
                html += "<td>-</td>"
        html += "</tr>"

    html += "</tbody></table></div>"
    return html


def build_table2(rows: list[dict]) -> str:
    """Table 2: Monthly IRR from NB regression."""
    html = '<div class="table-block">'
    html += '<p class="table-caption"><strong>Table 2.</strong> '
    html += "Monthly incidence rate ratios (IRR) from negative binomial "
    html += "regression (reference: December). All ages, 2009-2024. "
    html += "BH = Benjamini-Hochberg corrected significance. "
    html += "HAC IRR = Newey-West heteroscedasticity- and "
    html += "autocorrelation-consistent estimate.</p>"
    html += "<table><thead><tr>"
    html += "<th>Month</th><th>IRR</th><th>95% CI</th>"
    html += "<th>P</th><th>BH Sig.</th><th>HAC IRR</th>"
    html += "</tr></thead><tbody>"

    for r in rows:
        if r["month_label"] == "Dec":
            html += "<tr><td>Dec (ref)</td>"
            html += '<td class="num">1.000</td><td>-</td>'
            html += "<td>-</td><td>-</td>"
            html += '<td class="num">1.000</td></tr>'
            continue
        bold = ' style="font-weight:bold"' if r["month_label"] == "May" else ""
        html += f"<tr><td{bold}>{r['month_label']}</td>"
        html += f'<td class="num">{fmt(r["irr"])}</td>'
        html += f'<td class="num">{fmt(r["ci_low"])}-{fmt(r["ci_high"])}</td>'
        html += f'<td class="num">{fmt(r["p_value"], is_pvalue=True)}</td>'
        sig = "Yes" if r["bh_significant"] == "True" else "No"
        html += f"<td>{sig}</td>"
        html += f'<td class="num">{fmt(r["irr_hac"])}</td>'
        html += "</tr>"

    html += "</tbody></table></div>"
    return html


def build_table3(age_rows: list[dict], cause_rows: list[dict]) -> str:
    """Table 3: May IRR by age group and cause of death."""
    html = '<div class="table-block">'
    html += '<p class="table-caption"><strong>Table 3.</strong> '
    html += "May incidence rate ratios by age group and cause of death. "
    html += "Upper panel: age-stratified analysis. Lower panel: "
    html += "cause-stratified analysis. BH = Benjamini-Hochberg "
    html += "corrected significance.</p>"
    html += "<table><thead><tr>"
    html += "<th>Subgroup</th><th>May IRR</th><th>95% CI</th>"
    html += "<th>P</th><th>BH Sig.</th>"
    html += "</tr></thead><tbody>"

    html += '<tr><td colspan="5" style="background:#f0f0f0;'
    html += 'font-weight:bold">Age group</td></tr>'
    for r in age_rows:
        bold = ' style="font-weight:bold"' if r["age_group"] == "20-29" else ""
        html += f"<tr><td{bold}>{r['age_group']}</td>"
        html += f'<td class="num">{fmt(r["may_irr"])}</td>'
        html += f'<td class="num">{fmt(r["ci_low"])}-{fmt(r["ci_high"])}</td>'
        html += f'<td class="num">{fmt(r["p_value"], is_pvalue=True)}</td>'
        sig = "Yes" if r["bh_significant"] == "True" else "No"
        html += f"<td>{sig}</td></tr>"

    html += '<tr><td colspan="5" style="background:#f0f0f0;'
    html += 'font-weight:bold">Cause of death</td></tr>'
    for r in cause_rows:
        html += f"<tr><td>{r['cause']}</td>"
        html += f'<td class="num">{fmt(r["may_irr"])}</td>'
        html += f'<td class="num">{fmt(r["ci_low"])}-{fmt(r["ci_high"])}</td>'
        html += f'<td class="num">{fmt(r["p_value"], is_pvalue=True)}</td>'
        sig = "Yes" if r["bh_significant"] == "True" else "No"
        html += f"<td>{sig}</td></tr>"

    html += "</tbody></table></div>"
    return html


def build_table4(rows: list[dict]) -> str:
    """Table 4: Sensitivity analyses."""
    html = '<div class="table-block">'
    html += '<p class="table-caption"><strong>Table 4.</strong> '
    html += "Sensitivity analyses for May IRR. COVID exclusion, era "
    html += "comparison, and cause-specific analysis within the "
    html += "20-29 age group.</p>"
    html += "<table><thead><tr>"
    html += "<th>Analysis</th><th>May IRR</th><th>95% CI</th>"
    html += "<th>P</th><th>N obs</th>"
    html += "</tr></thead><tbody>"

    for r in rows:
        html += f"<tr><td>{r['analysis']}</td>"
        html += f'<td class="num">{fmt(r["may_irr"])}</td>'
        html += f'<td class="num">{fmt(r["ci_low"])}-{fmt(r["ci_high"])}</td>'
        html += f'<td class="num">{fmt(r["p_value"], is_pvalue=True)}</td>'
        html += f'<td class="num">{r["n_observations"]}</td>'
        html += "</tr>"

    html += "</tbody></table></div>"
    return html


def build_figures_html(legends: dict[str, str]) -> str:
    """Build HTML for figures section."""
    html = '<div style="page-break-before:always"></div>\n'
    html += "<h2>Figures</h2>\n"

    for fig_label, fig_file in FIGURE_FILES.items():
        fig_path = OUTPUT_DIR / fig_file
        if not fig_path.exists():
            print(f"[WARN] {fig_path} not found, skipping")
            continue
        caption = legends.get(fig_label, "")
        html += '<div class="figure-block">'
        html += f'<img src="file://{fig_path.resolve()}" alt="{fig_label}">'
        html += f'<p class="figure-caption"><strong>{fig_label}.</strong> '
        html += f"{caption}</p></div>\n"

    return html


def extract_figure_legends(md_text: str) -> dict[str, str]:
    """Extract figure legend text from manuscript."""
    legends = {}
    pattern = r'\*\*Figure (\d+)\.\*\*\s*(.*?)(?=\n\n|\*\*Figure|\Z)'
    for m in re.finditer(pattern, md_text, re.DOTALL):
        fig_num = m.group(1)
        text = m.group(2).strip().replace("\n", " ")
        legends[f"Figure {fig_num}"] = text
    return legends


def convert():
    md_text = MANUSCRIPT_MD.read_text(encoding="utf-8")

    # Extract figure legends before stripping them
    legends = extract_figure_legends(md_text)

    # Remove Figure Legends and Tables sections from main text
    # (they'll be rebuilt with actual content)
    md_text = re.sub(
        r"## Figure Legends.*",
        "",
        md_text,
        flags=re.DOTALL,
    )

    # Convert markdown to HTML
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "smarty"],
    )

    # Build tables from CSV
    t1_rows = read_csv(OUTPUT_DIR / "table1_descriptive.csv")
    t2_rows = read_csv(OUTPUT_DIR / "table2_monthly_irr.csv")
    t3_age = read_csv(OUTPUT_DIR / "table3_age_subgroup.csv")
    t3_cause = read_csv(OUTPUT_DIR / "table4_cause_subgroup.csv")
    t4_rows = read_csv(OUTPUT_DIR / "table5_sensitivity.csv")

    tables_html = '<div style="page-break-before:always"></div>\n'
    tables_html += "<h2>Tables</h2>\n"
    tables_html += build_table1(t1_rows)
    tables_html += build_table2(t2_rows)
    tables_html += build_table3(t3_age, t3_cause)
    tables_html += build_table4(t4_rows)

    # Build figures
    figures_html = build_figures_html(legends)

    # Assemble full HTML
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{html_body}{tables_html}{figures_html}</body></html>"""

    out_path = OUTPUT_DIR / "manuscript.pdf"
    weasyprint.HTML(string=html, base_url=str(PROJECT_DIR)).write_pdf(
        str(out_path)
    )
    print(f"[OK] {out_path}")


if __name__ == "__main__":
    convert()
