import os
import datetime
from weasyprint import HTML, CSS

def generate_pdf_report(data):
    # Prepare directory
    reports_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    filename = "eb1a_risk_report.pdf"
    filepath = os.path.join(reports_dir, filename)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    findings = data.get("rule_based_findings", [])
    repetitions = data.get("repetitive_letters", [])

    # Start HTML
    html = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    padding: 40px;
                    line-height: 1.6;
                    color: #333;
                }}
                h1, h2 {{
                    color: #003366;
                }}
                .low {{ color: green; font-weight: bold; }}
                .medium {{ color: orange; font-weight: bold; }}
                .high {{ color: red; font-weight: bold; }}
                .excerpt {{
                    font-style: italic;
                    background-color: #f1f1f1;
                    padding: 10px;
                    margin: 10px 0;
                    border-left: 4px solid #ccc;
                }}
                .recommendation {{
                    background-color: #e7f3fe;
                    padding: 10px;
                    border-left: 4px solid #2196F3;
                    margin-bottom: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th, td {{
                    border: 1px solid #ccc;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                .toc li {{
                    margin-bottom: 5px;
                }}
            </style>
        </head>
        <body>
            <h1>EB-1A RFE Risk Assessment Report</h1>
            <p><strong>Date:</strong> {now}</p>

            <h2>📘 Table of Contents</h2>
            <ul class="toc">
                <li>📊 Risk Matrix</li>
                <li>🧠 Rule-Based Findings</li>
                <li>⚠️ Repetitive Letters</li>
                <li>✅ Recommendations</li>
            </ul>

            <h2>📊 Risk Matrix</h2>
            <table>
                <tr>
                    <th>Criterion</th>
                    <th>Risk Level</th>
                    <th>Issues Detected</th>
                </tr>
    """

    # Risk Matrix
    for item in findings:
        criterion = item['matched_criterion']
        issues = item['issues']
        if len(issues) > 3:
            risk = '<span class="high">High</span>'
        elif len(issues) == 2 or len(issues) == 3:
            risk = '<span class="medium">Medium</span>'
        else:
            risk = '<span class="low">Low</span>'

        html += f"""
        <tr>
            <td>{criterion}</td>
            <td>{risk}</td>
            <td>{len(issues)}</td>
        </tr>
        """

    html += "</table>"

    # Rule-Based Findings
    html += "<h2>🧠 Rule-Based Findings</h2>"
    if findings:
        for item in findings:
            html += f"<h3>{item['matched_criterion']}</h3>"
            html += f"<p class='excerpt'>{item['excerpt']}</p>"
            html += "<ul>"
            for issue in item["issues"]:
                html += f"<li>{issue}</li>"
            html += "</ul>"
    else:
        html += "<p>No rule-based issues found.</p>"

    # Repetitive Letters
    html += "<h2>⚠️ Repetitive Recommendation Letters</h2>"
    if repetitions:
        html += "<ul>"
        for rep in repetitions:
            html += f"<li>{rep['letter_1']} ↔ {rep['letter_2']} — Similarity: {rep['similarity']:.2f}</li>"
        html += "</ul>"
    else:
        html += "<p>No significant repetition detected.</p>"

    # Recommendations
    html += "<h2>✅ Editable Recommendations</h2>"
    if findings:
        for item in findings:
            html += f"<div class='recommendation'><strong>Fix for {item['matched_criterion']}:</strong><br/><em>“Consider rephrasing the excerpt to explicitly state the impact, significance, or national/international recognition.”</em></div>"
    else:
        html += "<p>None needed. Looks great!</p>"

    html += "</body></html>"

    HTML(string=html).write_pdf(filepath)
    return filepath
