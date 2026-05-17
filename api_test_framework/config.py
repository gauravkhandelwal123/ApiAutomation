# config.py – central configuration for the API test framework

import os
from pathlib import Path

# Base directory of the framework (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory to store generated reports
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Path to the test definition file (YAML)
TEST_DEFINITIONS_PATH = BASE_DIR / "api_test_framework" / "tests.yaml"

# Report format: "html" or "markdown"
REPORT_FORMAT = "html"

# Run details
ENVIRONMENT = os.getenv("QA_ENV", "STAGING")
BUILD_SHA = os.getenv("BUILD_SHA", "latest-build")

# Email settings (optional). Set to None to disable email.
EMAIL_SETTINGS = {
    "enabled": False,
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "username": "user@example.com",
    "password": "password",
    "from_addr": "user@example.com",
    "to_addrs": ["recipient@example.com"],
}

# Scheduler settings – not used directly by the framework but handy for the batch script
SCHEDULE = {
    "task_name": "APITestFrameworkReport",
    "frequency": "DAILY",  # DAILY, WEEKLY, MONTHLY
    "start_time": "02:00",   # 24‑hour HH:MM format
}
