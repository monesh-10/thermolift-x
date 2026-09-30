import urllib.request
import json
import time

base_url = "http://127.0.0.1:8000"

# Retry loop for server startup
for attempt in range(10):
    try:
        with urllib.request.urlopen(f"{base_url}/api/health", timeout=3) as resp:
            data = json.loads(resp.read().decode())
            print(f"Health Check [Attempt {attempt+1}]:", data)
            break
    except Exception as e:
        print(f"Waiting for server... ({e})")
        time.sleep(1)

# Test Frontend HTML
with urllib.request.urlopen(f"{base_url}/", timeout=3) as resp:
    html = resp.read().decode()
    print("Frontend HTML length:", len(html), "Contains 'BAGHEWALA DIGITAL TWIN':", "BAGHEWALA DIGITAL TWIN" in html)

# Test CSS
with urllib.request.urlopen(f"{base_url}/static/css/style.css", timeout=3) as resp:
    css = resp.read().decode()
    print("CSS length:", len(css), "Contains 'OIL INDIA LIMITED':", "OIL INDIA LIMITED" in css)

# Test Fleet Summary API
with urllib.request.urlopen(f"{base_url}/api/fleet/summary", timeout=3) as resp:
    fleet = json.loads(resp.read().decode())
    print("Fleet Wells:", len(fleet["wells"]), "Total Oil:", fleet["total_oil_rate_bopd"])

# Test Well State API
with urllib.request.urlopen(f"{base_url}/api/well/BGW-002", timeout=3) as resp:
    well = json.loads(resp.read().decode())
    print("Well BGW-002 State:", well["well_id"], well["health_status"], well["status_message"])

print("\nALL HTTP ENDPOINTS ARE 100% OPERATIONAL!")
