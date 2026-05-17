import requests
import json
import sys
import os
import re
from typing import Any, Dict, Optional, List

def print_banner():
    print("=" * 60)
    print("       🚀 ADVANCED API TESTING & POSTMAN RUNNER")
    print("=" * 60)

def get_input(prompt: str, default: str = "") -> str:
    user_input = input(f"{prompt} [{default}]: ").strip()
    return user_input if user_input else default

def replace_variables(text: str, variables: Dict[str, str]) -> str:
    """Replace {{variable}} placeholders with values."""
    if not isinstance(text, str):
        return text
    for key, value in variables.items():
        text = text.replace(f"{{{{{key}}}}}", str(value))
    return text

def verify_json_response(actual: Any, expected: Any, path: str = "root") -> list:
    """Recursively compare two JSON objects and return differences."""
    differences = []
    
    if type(actual) != type(expected):
        differences.append(f"Type mismatch at {path}: expected {type(expected).__name__}, got {type(actual).__name__}")
        return differences

    if isinstance(actual, dict):
        for key in expected:
            if key not in actual:
                differences.append(f"Missing key at {path}: '{key}'")
            else:
                differences.extend(verify_json_response(actual[key], expected[key], f"{path}.{key}"))
    elif isinstance(actual, list):
        if len(actual) != len(expected):
            differences.append(f"List length mismatch at {path}: expected {len(expected)}, got {len(actual)}")
        else:
            for i, (a, e) in enumerate(zip(actual, expected)):
                differences.extend(verify_json_response(a, e, f"{path}[{i}]"))
    else:
        if actual != expected:
            differences.append(f"Value mismatch at {path}: expected '{expected}', got '{actual}'")
            
    return differences

def run_request(method: str, url: str, headers: Dict, payload: Any, expected_status: str = "200"):
    print(f"\n📡 Sending {method} to: {url}")
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=payload if payload else None,
            timeout=15
        )
        
        print(f"✅ Status Code: {response.status_code}")
        
        actual_json = None
        try:
            actual_json = response.json()
            # print("📦 Response Body Snippet:", json.dumps(actual_json, indent=4)[:200], "...")
        except ValueError:
            pass

        # Simple verification
        if str(response.status_code) == expected_status:
            print("✔️ Status Check: PASSED")
            return True, actual_json
        else:
            print(f"❌ Status Check: FAILED (Expected {expected_status}, got {response.status_code})")
            return False, actual_json
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def run_collection_items(items: List[Dict], variables: Dict[str, str], folder_path: str = ""):
    results = {"total": 0, "passed": 0, "failed": 0}
    
    for item in items:
        name = item.get("name", "Unnamed Request")
        full_name = f"{folder_path}/{name}" if folder_path else name
        
        # If it's a folder, recurse
        if "item" in item:
            print(f"\n📂 Entering Folder: {name}")
            sub_results = run_collection_items(item["item"], variables, full_name)
            results["total"] += sub_results["total"]
            results["passed"] += sub_results["passed"]
            results["failed"] += sub_results["failed"]
            continue

        # Process Request
        request = item.get("request")
        if not request:
            continue

        results["total"] += 1
        print(f"\n--- Testing: {full_name} ---")
        
        # Extract Method
        method = request.get("method", "GET")
        
        # Extract URL
        url_data = request.get("url")
        if isinstance(url_data, dict):
            url = url_data.get("raw", "")
        else:
            url = str(url_data)
        
        url = replace_variables(url, variables)
        
        # Extract Headers
        headers = {}
        for h in request.get("header", []):
            if not h.get("disabled", False):
                headers[h.get("key")] = replace_variables(h.get("value", ""), variables)
        
        # Extract Body
        body_data = request.get("body")
        payload = None
        if body_data and body_data.get("mode") == "raw":
            try:
                raw_body = replace_variables(body_data.get("raw", ""), variables)
                payload = json.loads(raw_body)
            except:
                payload = raw_body

        # Run
        success, _ = run_request(method, url, headers, payload)
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
            
    return results

def single_request_mode():
    url = get_input("Enter API URL")
    if not url: return
    
    method = get_input("Enter HTTP Method", "GET").upper()
    headers_str = get_input("Enter Headers (JSON)", "{}")
    payload_str = get_input("Enter Payload (JSON)", "")
    
    headers = json.loads(headers_str) if headers_str else {}
    payload = json.loads(payload_str) if payload_str else None
    
    expected_status = get_input("Expected Status Code", "200")
    expected_response_str = get_input("Expected Response JSON (optional)")

    success, actual_json = run_request(method, url, headers, payload, expected_status)
    
    if expected_response_str and actual_json:
        diffs = verify_json_response(actual_json, json.loads(expected_response_str))
        if not diffs:
            print("✔️ Body Verification: PASSED")
        else:
            print("❌ Body Verification: FAILED")
            for d in diffs: print(f"  - {d}")

def postman_mode():
    file_path = get_input("Enter path to Postman Collection (.json)")
    if not os.path.exists(file_path):
        print("❌ File not found.")
        return

    env_path = get_input("Enter path to Environment Variables (.json) or press Enter to skip")
    variables = {}
    if env_path and os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            env_data = json.load(f)
            # Postman environments have 'values' list
            for item in env_data.get("values", []):
                variables[item["key"]] = item["value"]
    
    # Also allow manual variable input
    manual_vars = get_input("Enter extra variables (JSON format e.g. {\"baseUrl\": \"...\"})", "{}")
    if manual_vars:
        try:
            variables.update(json.loads(manual_vars))
        except: pass

    with open(file_path, 'r', encoding='utf-8') as f:
        collection = json.load(f)
        
    print(f"\n🚀 Running Collection: {collection.get('info', {}).get('name', 'Unnamed')}")
    results = run_collection_items(collection.get("item", []), variables)
    
    print("\n" + "=" * 60)
    print("📊 FINAL COLLECTION SUMMARY")
    print("=" * 60)
    print(f"Total Requests: {results['total']}")
    print(f"Passed:         {results['passed']}")
    print(f"Failed:         {results['failed']}")
    print("=" * 60)

def main():
    while True:
        print_banner()
        print("1. Run Single API Request")
        print("2. Run Postman Collection")
        print("3. Exit")
        choice = get_input("Select an option", "1")
        
        if choice == "1":
            single_request_mode()
        elif choice == "2":
            postman_mode()
        elif choice == "3":
            break
        else:
            print("Invalid choice.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
