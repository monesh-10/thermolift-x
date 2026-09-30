"""Field Steam Allocation Engine: Optimizes Field-Wide Steam Distribution.
Determines which wells should receive steam allocations under constrained boiler generation capacity.

Concept:
Marginal Value of Steam (MVS) = (Incremental Oil bbl / Steam Required m3) * (1 - Risk) * Confidence * Profit Margin

Answers:
1. Which well should receive the next unit of steam?
2. Why one well receives steam while another does not?
3. What is the fleet-wide incremental production and SOR?
"""

from typing import Dict, Any, List, Optional
import math


class SteamAllocationEngine:
    @classmethod
    def allocate_fleet_steam(
        cls,
        fleet_wells: Dict[str, Dict[str, Any]],
        available_steam_m3: float = 8500.0,
        steam_cost_per_m3: float = 1250.0,
        oil_price_per_bbl: float = 6200.0
    ) -> Dict[str, Any]:
        """Calculates optimal steam distribution across all Baghewala wells."""
        candidates: List[Dict[str, Any]] = []

        for well_id, w in sorted(fleet_wells.items()):
            temp = w.get("reservoir", {}).get("temperature_c", 50.0)
            visc = w.get("reservoir", {}).get("oil_viscosity_cp", 3000.0)
            oil = w.get("reservoir", {}).get("oil_rate_bopd", 30.0)
            p7d = w.get("failure_prediction", {}).get("prob_failure_7d", 0.10)
            is_floating = w.get("mechanics", {}).get("is_rod_floating", False)
            cycle_no = w.get("cycle_no", 1)

            # Thermal state classification
            if temp >= 120.0:
                thermal_state = "HOT"
                thermal_color = "#EF4444"
                steam_urgency = 0.10  # Still hot, doesn't need steam yet
            elif temp >= 85.0:
                thermal_state = "WARM"
                thermal_color = "#F59E0B"
                steam_urgency = 0.35
            elif temp >= 65.0:
                thermal_state = "TRANSITION"
                thermal_color = "#38BDF8"
                steam_urgency = 0.70
            elif temp >= 52.0:
                thermal_state = "COOLING"
                thermal_color = "#818CF8"
                steam_urgency = 0.95
            else:
                thermal_state = "CRITICAL"
                thermal_color = "#EC4899"
                steam_urgency = 1.00  # Severe viscosity freeze

            # Steam required (typically 1,400 to 2,200 m3 CWE depending on depth and cycle)
            pump_depth = w.get("metadata", {}).get("Pump_Depth_m", 1000.0)
            steam_req = round(1200.0 + (pump_depth / 1000.0) * 400.0 + (cycle_no * 50.0), 0)

            # Projected incremental oil over 90 days if steamed
            # Wells in COOLING / TRANSITION with low mechanical risk respond best
            response_factor = steam_urgency * (1.2 if not is_floating else 0.8)
            incremental_oil_bbl = round(oil * 90.0 * (0.85 + 0.45 * response_factor), 0)

            # Projected SOR
            sor = round(steam_req / max(1.0, incremental_oil_bbl * 0.158987), 2)

            # Reliability & risk penalty
            risk_penalty = min(0.60, p7d + (0.30 if is_floating else 0.0))

            # Confidence score
            confidence = 0.92 if thermal_state in ["COOLING", "TRANSITION"] else 0.84

            # Marginal Value of Steam (MVS)
            # Net economic return per m3 of steam allocated
            gross_oil_val = incremental_oil_bbl * oil_price_per_bbl
            steam_gen_cost = steam_req * steam_cost_per_m3
            net_gain_inr = (gross_oil_val - steam_gen_cost) * (1.0 - risk_penalty) * confidence
            marginal_value = round(net_gain_inr / max(1.0, steam_req), 1)

            candidates.append({
                "well_id": well_id,
                "current_oil_bopd": round(oil, 1),
                "temperature_c": round(temp, 1),
                "viscosity_cp": round(visc, 1),
                "thermal_state": thermal_state,
                "thermal_color": thermal_color,
                "steam_required_m3": steam_req,
                "incremental_oil_bbl": incremental_oil_bbl,
                "projected_sor": sor,
                "failure_risk_p7d": round(p7d, 2),
                "is_rod_floating": is_floating,
                "confidence": confidence,
                "marginal_value_inr_per_m3": marginal_value,
                "allocated": False,
                "allocated_steam_m3": 0.0,
                "allocation_rank": 0,
                "recommendation": "DEFER",
                "allocation_reason": ""
            })

        # Rank candidates by Marginal Value of Steam
        candidates.sort(key=lambda x: x["marginal_value_inr_per_m3"], reverse=True)

        # Greedy Knapsack Steam Allocation
        remaining_steam = available_steam_m3
        total_incremental_oil = 0.0
        total_allocated_steam = 0.0

        for rank, c in enumerate(candidates, start=1):
            c["allocation_rank"] = rank
            if c["thermal_state"] == "HOT":
                c["recommendation"] = "HOLD CURRENT (STILL HOT)"
                c["allocation_reason"] = f"Wellbore temperature ({c['temperature_c']}°C) is above viscosity threshold. Steam injection now would waste thermal energy."
            elif remaining_steam >= c["steam_required_m3"] and c["marginal_value_inr_per_m3"] > 0:
                c["allocated"] = True
                c["allocated_steam_m3"] = c["steam_required_m3"]
                c["recommendation"] = "ALLOCATE STEAM"
                c["allocation_reason"] = f"Top priority rank #{rank}: High thermal response with projected net return of ₹{c['marginal_value_inr_per_m3']:,.0f}/m³ steam."
                remaining_steam -= c["steam_required_m3"]
                total_allocated_steam += c["steam_required_m3"]
                total_incremental_oil += c["incremental_oil_bbl"]
            elif remaining_steam > 0:
                c["recommendation"] = "PARTIAL / DEFERRED"
                c["allocation_reason"] = f"Insufficient boiler capacity remaining ({remaining_steam:,.0f} m³ remaining vs {c['steam_required_m3']:,.0f} m³ required)."
            else:
                c["recommendation"] = "DEFER TO NEXT BATCH"
                c["allocation_reason"] = "Field steam capacity exhausted for current cycle. Queue for next operational batch."

        avg_fleet_sor = round(total_allocated_steam / max(1.0, total_incremental_oil * 0.158987), 2)
        total_net_value_lakhs = round(((total_incremental_oil * oil_price_per_bbl) - (total_allocated_steam * steam_cost_per_m3)) / 100000.0, 2)

        allocated_wells = [c["well_id"] for c in candidates if c["allocated"]]
        deferred_wells = [c["well_id"] for c in candidates if not c["allocated"] and c["thermal_state"] != "HOT"]

        why_summary = (
            f"Allocated {total_allocated_steam:,.0f} m³ CWE across {len(allocated_wells)} candidate wells "
            f"({', '.join(allocated_wells[:4])}{'...' if len(allocated_wells) > 4 else ''}) with the steepest marginal oil lift per unit steam. "
            f"Deferred {len(deferred_wells)} wells to safeguard boiler quota and maintain fleet-wide SOR at an efficient {avg_fleet_sor:.2f}."
        )

        return {
            "available_steam_m3": available_steam_m3,
            "total_allocated_steam_m3": total_allocated_steam,
            "unallocated_steam_m3": round(remaining_steam, 0),
            "allocated_wells_count": len(allocated_wells),
            "total_incremental_oil_bbl": round(total_incremental_oil, 0),
            "projected_fleet_sor": avg_fleet_sor,
            "projected_net_value_lakhs_inr": total_net_value_lakhs,
            "why_summary": why_summary,
            "allocation_table": candidates
        }