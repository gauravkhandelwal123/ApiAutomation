# report_generator.py – Generates a premium HTML report for API test results

import os
from datetime import datetime
from pathlib import Path


def _header_html():
    """Return a stylish header with gradient background."""
    return """
    <div style="
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        padding: 20px;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    ">
        <h1 style="margin:0; font-size:2rem;">API Test Execution Report</h1>
        <p style="margin:4px 0; font-size:1rem;">Generated on {now}</p>
    </div>
    """.format(now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def _table_html(results):
    rows = []
    for r in results:
        color = "#4caf50" if r["success"] else "#f44336"
        status = "PASS" if r["success"] else "FAIL"
        rows.append(f"""
        <tr style='background:{color}20'>
            <td style='padding:8px;'>{r['name']}</td>
            <td style='padding:8px;'>{r['method']}</td>
            <td style='padding:8px;'>{r['url']}</td>
            <td style='padding:8px; font-weight:bold; color:{color}'>{status}</td>
            <td style='padding:8px;'>{r['details'].get('error', '') or ''}</td>
        </tr>
        """)
    # generate HTML table
    return f"""<table style=\"width:100%; border-collapse:collapse; font-family: 'Segoe UI', Tahoma, sans-serif;\">
        <thead>
            <tr style='background:#333; color:white;'>
                <th style='padding:8px; text-align:left;'>Test Name</th>
                <th style='padding:8px; text-align:left;'>Method</th>
                <th style='padding:8px; text-align:left;'>URL</th>
                <th style='padding:8px; text-align:left;'>Result</th>
                <th style='padding:8px; text-align:left;'>Error / Details</th>
            </tr>
        </thead>
        <tbody>
            {"\n".join(rows)}
        </tbody>
    </table>
    """


def generate_report(results, config):
    """Create an HTML report file in config.REPORTS_DIR and return its path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = config.REPORTS_DIR / f"api_test_report_{timestamp}.html"
    html_content = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>API Test Report – {timestamp}</title>
        <style>
            body {{ background:#f0f2f5; margin:0; padding:20px; font-family:'Segoe UI', Tahoma, sans-serif; }}
            .container {{ max-width:1200px; margin:auto; background:white; border-radius:8px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.1); }}
            a {{ color:#1e90ff; }}
        </style>
    </head>
    <body>
        <div class='container'>
            {_header_html()}
            <br/>
            {_table_html(results)}
        </div>
    </body>
    </html>
    """
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    return str(report_file)

# Export the function for imports
__all__ = ["generate_report"]
