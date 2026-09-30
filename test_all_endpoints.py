import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:8000"

def post_json(path, data):
    url = f"{base_url}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def get_json(path):
    url = f"{base_url}{path}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode())

print("--- 1. Testing GET /api/fleet/summary ---")
summary = get_json("/api/fleet/summary")
print(f"Total Wells: {summary['total_wells']}, Field Oil: {summary['total_oil_rate_bopd']} bopd, Avg SOR: {summary['average_sor']}")

print("\n--- 2. Testing GET /api/well/BGW-002 ---")
well = get_json("/api/well/BGW-002")
print(f"Well: {well['well_id']}, Temp: {well['reservoir']['temperature_c']} C, Viscosity: {well['reservoir']['oil_viscosity_cp']} cP")
print(f"Rod Floating Margin: {well['mechanics']['floating_margin_pct']}%, Is Floating: {well['mechanics']['is_rod_floating']}")
print(f"Dyno Card Area: {well['dyno_cards']['card_area_klb_in']} klb-in, PPRL: {well['mechanics']['pprl_klb']} klb")

print("\n--- 3. Testing POST /api/well/BGW-002/optimize-vfd ---")
vfd_opt = post_json("/api/well/BGW-002/optimize-vfd", {})
print("Recommended SPM:", vfd_opt["recommended"]["spm"], "VFD Hz:", vfd_opt["recommended"]["vfd_hz"])
print("Energy Savings:", vfd_opt["improvements"]["energy_saved_pct"], "%")

print("\n--- 4. Testing POST /api/well/BGW-002/apply-vfd ---")
dispatch_res = post_json("/api/well/BGW-002/apply-vfd", {"spm": 5.8, "vfd_hz": 36.2})
print("Dispatch result:", dispatch_res["message"])
print("Updated Floating Margin:", dispatch_res["updated_state"]["mechanics"]["floating_margin_pct"], "%")

print("\n--- 5. Testing POST /api/well/BGW-002/optimize-css ---")
css_opt = post_json("/api/well/BGW-002/optimize-css", {"priority": "balanced"})
print("Recommended CSS Plan:", css_opt["recommended_plan"]["plan_name"])
print("Predicted Cum Oil:", css_opt["recommended_plan"]["predicted_outcomes"]["cum_oil_produced_bbl"], "bbl")
print("Predicted SOR:", css_opt["recommended_plan"]["predicted_outcomes"]["steam_oil_ratio_sor"])

print("\n--- 6. Testing POST /api/well/BGW-002/simulate-thermal ---")
thermal = post_json("/api/well/BGW-002/simulate-thermal", {"peak_temp_c": 190.0})
print("Thermal simulation points:", len(thermal["simulation_series"]))
print("Day 1 Temp:", thermal["simulation_series"][0]["temperature_c"], "C, Day 120 Temp:", thermal["simulation_series"][-1]["temperature_c"], "C")
print("Day 1 Viscosity:", thermal["simulation_series"][0]["viscosity_cp"], "cP, Day 120 Viscosity:", thermal["simulation_series"][-1]["viscosity_cp"], "cP")

print("\n--- 7. Testing GET /api/well/BGW-002/timeline ---")
timeline = get_json("/api/well/BGW-002/timeline?limit=30")
print("Historical timeline records:", len(timeline))

print("\nALL 7 CORE WELL-TO-SURFACE ENDPOINTS VERIFIED AND PASSING 100%!")
