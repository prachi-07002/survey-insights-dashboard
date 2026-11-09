"""Static HTML report generator.

Builds a single self-contained report.html (inline CSS, no JavaScript,
no external resources) with summary tables and CSS bar charts showing
Likert distributions and per-group means.
"""

import html

CSS = """
body { font-family: Georgia, 'Times New Roman', serif; max-width: 900px;
       margin: 0 auto; padding: 24px; color: #222; background: #fdfbf7; }
h1 { color: #5b2a86; border-bottom: 3px solid #5b2a86; padding-bottom: 8px; }
h2 { color: #5b2a86; margin-top: 36px; }
h3 { color: #333; margin-top: 24px; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th, td { border: 1px solid #ccc; padding: 8px 10px; text-align: left; }
th { background: #efe6f7; }
tr:nth-child(even) td { background: #f7f3fb; }
.bar-row { display: flex; align-items: center; margin: 4px 0; }
.bar-label { width: 140px; flex-shrink: 0; }
.bar-track { flex: 1; background: #eee; height: 18px; border-radius: 4px; }
.bar-fill { background: #7b4ba6; height: 18px; border-radius: 4px; }
.bar-value { width: 70px; text-align: right; flex-shrink: 0; }
.note { color: #555; font-size: 0.9em; }
"""

ITEM_LABELS = {
    "confidence": "Confidence",
    "engagement": "Engagement",
    "perceived_fairness": "Perceived fairness",
    "genai_usefulness": "GenAI usefulness",
}


def _esc(text):
    return html.escape(str(text))


def _bar(label, value, max_value, value_text):
    pct = (value / max_value * 100) if max_value else 0
    return (
        f'<div class="bar-row"><span class="bar-label">{_esc(label)}</span>'
        f'<span class="bar-track"><span class="bar-fill" '
        f'style="display:block;width:{pct:.1f}%"></span></span>'
        f'<span class="bar-value">{_esc(value_text)}</span></div>'
    )


def generate_report(rows, overall, breakdown, comparisons, kw_summary, output_path):
    """Write the full HTML report and return the output path."""
    n = len(rows)
    groups = sorted(breakdown)
    parts = []
    parts.append("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n")
    parts.append("<title>Survey Insights Report — STEM Education Interventions</title>\n")
    parts.append(f"<style>{CSS}</style>\n</head>\n<body>\n")
    parts.append("<h1>Survey Insights Report</h1>\n")
    parts.append("<p>Qualitative + Likert-scale survey analysis of three STEM "
                 "education interventions: GenAI in Project Management, "
                 "Social Justice in Calculus, and the PMaster Game.</p>\n")
    parts.append(f"<p><strong>Respondents (N):</strong> {n} &nbsp;|&nbsp; "
                 "<strong>Data:</strong> fictional sample survey "
                 "(data/sample_survey.csv)</p>\n")

    # Sample sizes
    parts.append("<h2>Sample sizes by intervention group</h2>\n<table>\n"
                 "<tr><th>Intervention group</th><th>N</th><th>Share</th></tr>\n")
    for group in groups:
        g_n = sum(1 for r in rows if r["intervention_group"] == group)
        parts.append(f"<tr><td>{_esc(group)}</td><td>{g_n}</td>"
                     f"<td>{g_n / n * 100:.0f}%</td></tr>\n")
    parts.append("</table>\n")

    # Overall means
    parts.append("<h2>Overall results (all groups combined)</h2>\n<table>\n"
                 "<tr><th>Item</th><th>N</th><th>Mean</th><th>Median</th>"
                 "<th>Std dev</th></tr>\n")
    for item, s in overall.items():
        parts.append(f"<tr><td>{_esc(ITEM_LABELS.get(item, item))}</td>"
                     f"<td>{s['n']}</td><td>{s['mean']:.2f}</td>"
                     f"<td>{s['median']:.1f}</td><td>{s['std']:.2f}</td></tr>\n")
    parts.append("</table>\n")
    for item, s in overall.items():
        parts.append(f"<h3>{_esc(ITEM_LABELS.get(item, item))} — distribution (1–5)</h3>\n")
        for score in (1, 2, 3, 4, 5):
            count = s["distribution"][score]
            parts.append(_bar(f"Score {score}", count, n, f"{count} ({count / n * 100:.0f}%)"))
        parts.append("\n")

    # Group comparison
    parts.append("<h2>Group comparison</h2>\n<table>\n"
                 "<tr><th>Item</th>"
                 + "".join(f"<th>{_esc(g)}</th>" for g in groups)
                 + "<th>Largest gap</th></tr>\n")
    for item, comp in comparisons.items():
        cells = "".join(f"<td>{comp['means'][g]:.2f}</td>" for g in groups)
        parts.append(f"<tr><td>{_esc(ITEM_LABELS.get(item, item))}</td>{cells}"
                     f"<td>{comp['difference']:.2f} "
                     f"({ _esc(comp['highest_group'])} vs "
                     f"{_esc(comp['lowest_group'])})</td></tr>\n")
    parts.append("</table>\n")
    for item, comp in comparisons.items():
        parts.append(f"<h3>{_esc(ITEM_LABELS.get(item, item))} — mean by group</h3>\n")
        for group in groups:
            parts.append(_bar(group, comp["means"][group], 5.0, f"{comp['means'][group]:.2f}"))
        parts.append("\n")

    # Keywords
    parts.append("<h2>Open-ended responses — top keywords</h2>\n<table>\n"
                 "<tr><th>Keyword</th><th>Mentions</th></tr>\n")
    for word, count in kw_summary["overall"]:
        parts.append(f"<tr><td>{_esc(word)}</td><td>{count}</td></tr>\n")
    parts.append("</table>\n")
    for group in groups:
        parts.append(f"<h3>{_esc(group)}</h3>\n<table>\n"
                     "<tr><th>Keyword</th><th>Mentions</th></tr>\n")
        for word, count in kw_summary["by_group"][group]:
            parts.append(f"<tr><td>{_esc(word)}</td><td>{count}</td></tr>\n")
        parts.append("</table>\n")

    parts.append("<p class=\"note\">All data in this report is fictional sample "
                 "data created for demonstration purposes; no real personal data "
                 "is included.</p>\n</body>\n</html>\n")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(parts))
    return output_path
