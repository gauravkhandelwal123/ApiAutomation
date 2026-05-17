# email_sender.py – Sends automated email reports

import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path


def send_report(report_path, config, stats):
    """Send an email notification with execution summary and the attached HTML report."""
    email_settings = getattr(config, "EMAIL_SETTINGS", {})
    if not email_settings or not email_settings.get("enabled"):
        return

    # Extract settings
    smtp_server = email_settings.get("smtp_server")
    smtp_port = email_settings.get("smtp_port", 587)
    username = email_settings.get("username")
    password = email_settings.get("password")
    from_addr = email_settings.get("from_addr")
    to_addrs = email_settings.get("to_addrs", [])
    
    if not smtp_server or not from_addr or not to_addrs:
        print("Incomplete email configuration. Cannot send email.")
        return

    # Determine overall status
    status = "PASS" if stats.get("failed", 0) == 0 else "FAIL"
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Subject: [ADGRID QA] Nightly Regression — PASS|FAIL — <YYYY-MM-DD>
    subject = f"[ADGRID QA] Nightly Regression — {status} — {date_str}"
    
    # Body
    env = getattr(config, "ENVIRONMENT", "N/A")
    build = getattr(config, "BUILD_SHA", "N/A")
    total = stats.get("total", 0)
    passed = stats.get("passed", 0)
    failed = stats.get("failed", 0)
    skipped = stats.get("skipped", 0)
    duration = stats.get("duration_str", "0s")
    
    body = f"""API Test Execution Summary
==========================
Environment: {env}
Build/Commit SHA: {build}
Duration: {duration}

Total Tests: {total}
Passed: {passed}
Failed: {failed}
Skipped: {skipped}

"""
    failures = stats.get("failures", [])
    if failures:
        body += "Failing Tests:\n"
        body += "--------------\n"
        for f in failures:
            # Get one-line excerpt of error
            error_excerpt = f["error"].split('\n')[0] if isinstance(f["error"], str) else str(f["error"])
            # truncate if too long
            if len(error_excerpt) > 100:
                error_excerpt = error_excerpt[:97] + "..."
            body += f"- {f['name']}: {error_excerpt}\n"
    else:
        body += "All tests passed successfully.\n"

    body += "\nPlease find the full HTML report attached."

    # Construct the message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ", ".join(to_addrs)
    msg.set_content(body)

    # Attach the HTML report
    report_file = Path(report_path)
    if report_file.exists():
        with open(report_file, 'rb') as f:
            report_data = f.read()
        msg.add_attachment(
            report_data,
            maintype='text',
            subtype='html',
            filename=report_file.name
        )

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise e

__all__ = ["send_report"]
