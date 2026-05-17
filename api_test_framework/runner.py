# runner.py – Executes API tests defined in tests.yaml and generates a report

import importlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
import yaml

# Import local modules
import config
import report_generator


def load_test_definitions():
    """Load test cases from the YAML file defined in config.TEST_DEFINITIONS_PATH."""
    with open(config.TEST_DEFINITIONS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def evaluate_assertions(response_json, assertions):
    """Very simple assertions evaluator.
    ``assertions`` is a dict where the key is a dotted path (e.g. ``json.key`` or ``args.foo``)
    and the value is the expected value.
    Returns ``True`` if all match, otherwise ``False`` and a list of mismatches.
    """
    mismatches = []
    for path, expected in assertions.items():
        # Resolve dotted path
        parts = path.split('.')
        current = response_json
        for p in parts:
            if isinstance(current, dict) and p in current:
                current = current[p]
            else:
                mismatches.append(f"Path '{path}' not found in response")
                current = None
                break
        if current != expected:
            mismatches.append(f"{path}: expected {expected!r}, got {current!r}")
    return len(mismatches) == 0, mismatches


def run_tests():
    test_cases = load_test_definitions()
    results = []
    for case in test_cases:
        name = case.get("name", "Unnamed test")
        method = case.get("method", "GET").upper()
        url = case["url"]
        headers = case.get("headers", {})
        payload = case.get("payload", {})
        expected_status = case.get("expected_status", 200)
        assertions = case.get("assertions", {})

        try:
            resp = requests.request(method, url, headers=headers, json=payload, timeout=30)
            status_ok = resp.status_code == expected_status
            json_resp = {}
            try:
                json_resp = resp.json()
            except Exception:
                pass
            assertions_ok, mismatches = evaluate_assertions(json_resp, assertions) if assertions else (True, [])
            success = status_ok and assertions_ok
            details = {
                "status_code": resp.status_code,
                "status_ok": status_ok,
                "assertions_ok": assertions_ok,
                "mismatches": mismatches,
                "response": json_resp,
            }
        except Exception as e:
            success = False
            details = {"error": str(e)}

        results.append({
            "name": name,
            "method": method,
            "url": url,
            "success": success,
            "details": details,
        })
    return results


def main():
    results = run_tests()
    # Generate report
    report_path = report_generator.generate_report(results, config)
    print(f"Report generated: {report_path}")
    # Optional email – skipped unless EMAIL_SETTINGS["enabled"] is True
    if config.EMAIL_SETTINGS.get("enabled"):
        try:
            from . import email_sender  # you may create this module later
            email_sender.send_report(report_path, config)
        except Exception as e:
            print(f"Failed to send email: {e}")


if __name__ == "__main__":
    main()
