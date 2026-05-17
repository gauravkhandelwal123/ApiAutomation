# report_generator.py – Generates an ExtentReports-style premium HTML report

import os
from datetime import datetime
from pathlib import Path


def _header_html(config, stats):
    """Return a stylish dashboard header resembling ExtentReports."""
    env = getattr(config, "ENVIRONMENT", "N/A")
    build = getattr(config, "BUILD_SHA", "N/A")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    total = stats.get("total", 0) if stats else 0
    passed = stats.get("passed", 0) if stats else 0
    failed = stats.get("failed", 0) if stats else 0
    duration = stats.get("duration_str", "0s") if stats else "0s"
    
    pass_pct = (passed / total * 100) if total > 0 else 0
    
    return f"""
    <div class="header">
        <div class="title-area">
            <h1>API Automation Report</h1>
            <p>Generated: {now} | Environment: <strong>{env}</strong> | Build: <strong>{build}</strong></p>
        </div>
    </div>
    
    <div class="dashboard">
        <div class="card" style="border-top: 4px solid #2196f3;">
            <h3>Total Tests</h3>
            <div class="value">{total}</div>
        </div>
        <div class="card" style="border-top: 4px solid #4caf50;">
            <h3>Passed</h3>
            <div class="value" style="color: #4caf50;">{passed}</div>
        </div>
        <div class="card" style="border-top: 4px solid #f44336;">
            <h3>Failed</h3>
            <div class="value" style="color: #f44336;">{failed}</div>
        </div>
        <div class="card" style="border-top: 4px solid #ff9800;">
            <h3>Pass Rate</h3>
            <div class="value" style="color: #ff9800;">{pass_pct:.1f}%</div>
        </div>
        <div class="card" style="border-top: 4px solid #9c27b0;">
            <h3>Duration</h3>
            <div class="value" style="color: #9c27b0; font-size: 1.5rem; line-height: 2.2rem;">{duration}</div>
        </div>
    </div>
    """


def _table_html(results):
    rows = []
    for r in results:
        color = "#4caf50" if r["success"] else "#f44336"
        status_badge = f"<span class='badge' style='background:{color};'>{ 'PASS' if r['success'] else 'FAIL' }</span>"
        
        # Format the JSON response if available, otherwise just error string
        error_details = r['details'].get('error', '')
        if not error_details and r['details'].get('mismatches'):
            error_details = "<br>".join(r['details']['mismatches'])
        
        details_html = f"<div class='error-text'>{error_details}</div>" if error_details else "<div style='color:#777;'>No errors</div>"
        
        rows.append(f"""
        <div class="test-row">
            <div class="test-header">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="test-name">{r['name']}</div>
                    <div>{status_badge}</div>
                </div>
                <div class="test-meta">
                    <span class="method {r['method']}">{r['method']}</span>
                    <a href='{r['url']}' target='_blank'>{r['url']}</a>
                </div>
            </div>
            <div class="test-body">
                {details_html}
            </div>
        </div>
        """)
    return f"""<div class="test-list">{"".join(rows)}</div>"""


def generate_report(results, config, stats=None):
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
            :root {{
                --bg: #f4f6f8;
                --card-bg: #ffffff;
                --text-main: #333333;
                --text-muted: #666666;
                --border: #e0e0e0;
            }}
            body {{
                background: var(--bg);
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                color: var(--text-main);
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: var(--card-bg);
                padding: 20px 30px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                margin-bottom: 20px;
                border-left: 5px solid #2c3e50;
            }}
            .header h1 {{ margin: 0 0 10px 0; font-size: 24px; color: #2c3e50; }}
            .header p {{ margin: 0; color: var(--text-muted); font-size: 14px; }}
            
            .dashboard {{
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .card {{
                flex: 1;
                background: var(--card-bg);
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                text-align: center;
            }}
            .card h3 {{ margin: 0 0 10px 0; font-size: 14px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
            .card .value {{ font-size: 28px; font-weight: bold; }}
            
            .test-list {{
                display: flex;
                flex-direction: column;
                gap: 15px;
            }}
            .test-row {{
                background: var(--card-bg);
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                overflow: hidden;
            }}
            .test-header {{
                padding: 15px 20px;
                border-bottom: 1px solid var(--border);
                background: #fafafa;
            }}
            .test-name {{
                font-weight: 600;
                font-size: 16px;
                color: #2c3e50;
            }}
            .badge {{
                color: white;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            .test-meta {{
                margin-top: 8px;
                font-size: 13px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .method {{
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 11px;
                color: white;
            }}
            .method.GET {{ background: #61affe; }}
            .method.POST {{ background: #49cc90; }}
            .method.PUT {{ background: #fca130; }}
            .method.DELETE {{ background: #f93e3e; }}
            .test-meta a {{
                color: #0366d6;
                text-decoration: none;
                word-break: break-all;
            }}
            .test-meta a:hover {{ text-decoration: underline; }}
            .test-body {{
                padding: 15px 20px;
                font-size: 14px;
                background: #ffffff;
            }}
            .error-text {{
                color: #d32f2f;
                font-family: monospace;
                white-space: pre-wrap;
                background: #ffebee;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #ffcdd2;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {_header_html(config, stats)}
            <h2 style="font-size:18px; margin:0 0 15px 0; color:#2c3e50;">Test Execution Details</h2>
            {_table_html(results)}
        </div>
    </body>
    </html>
    """
    
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    return str(report_file)

__all__ = ["generate_report"]
