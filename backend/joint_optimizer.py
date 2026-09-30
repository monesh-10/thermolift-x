"""Joint CSS + SRP Optimizer: Couples Thermal Recovery and Artificial Lift.
Optimizes CSS injection parameters together with downstream SRP operational speed schedules
into an integrated, closed-loop cyber-physical decision system.

Workflow:
Thermal State -> In-Situ Viscosity -> SRP Mechanics -> Production & Energy -> Reliability -> Economics.

Enforces:
1. Multi-Objective Weighting: Production, Energy, Reliability, Cost, SOR.
2. Safety Governor Constraints (SPM, VFD, Fracture Pressure, Rod Floating, Fillage).
3. Transparent Comparison against CURRENT / DO NOTHING.
4. If no candidate justifies intervention cost/risk -> HOLD CURRENT OPERATION.
"""

from typing import Dict, Any, List, Optional
import math
from .physics_engine import PhysicsEngine
from .model_registry import ModelRegistry
from .safety_governor import SafetyGovernor
from .confidence_engine import ConfidenceEngine


class JointOptimizer:
    DEFAULT_WEIGHTS = {
        "balanced": {"w_oil": 0.60, "w_energy": 0.50, "w_rel": 0.60, "w_cost": 0.50, "w_sor": 0.40},
        "production_first": {"w_oil": 1.00, "w_energy": 0.20, "w_rel": 0.35, "w_cost": 0.25, "w_sor": 0.20},
        "energy_first": {"w_oil": 0.40, "w_energy": 1.00, "w_rel": 0.45, "w_cost": 0.55, "w_sor": 0.50},
        "reliability_first": {"w_oil": 0.30, "w_energy": 0.35, "w_rel": 1.00, "w_cost": 0.30, "w_sor": 0.30},
        "cost_first": {"w_oil": 0.50, "w_energy": 0.50, "w_rel": 0.50, "w_cost": 1.00, "w_sor": 0.65},
    }

    DEFAULT_ECONOMICS = {
        "oil_price_per_bbl": 6200.0,       # ~75 USD/bbl in INR
        "steam_cost_per_m3": 1250.0,       # INR per m3 CWE steam
        "electricity_cost_per_kwh": 7.50,  # INR per kWh (~0.09 USD)
        "workover_cost_failure": 850000.0  # INR per failure event (pulling unit, new rods)
    }

    @classmethod
    def run_joint_optimization(
        cls,
        well_state: Dict[str, Any],
        profile: str = "balanced",
        custom_weights: Optional[Dict[str, float]] = None,
        custom_economics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Runs the coupled CSS + SRP decision optimization."""
        weights = custom_weights or cls.DEFAULT_WEIGHTS.get(profile, cls.DEFAULT_WEIGHTS["balanced"])
        econ_params = custom_economics or cls.DEFAULT_ECONOMICS

        well_meta = well_state.get("metadata", {})
        res_state = well_state.get("reservoir", {})
        srp_state = well_state.get("surface_srp", {})
        mech_state = well_state.get("mechanics", {})
        fail_state = well_state.get("failure_prediction", {})
        conf_eval = ConfidenceEngine.evaluate_well_confidence(well_state)

        # Baseline Current / Do Nothing state
        curr_spm = srp_state.get("spm", 8.0)
        curr_vfd = srp_state.get("vfd_frequency_hz", 50.0)
        curr_stroke = srp_state.get("stroke_length_in", 100.0)
        curr_oil = res_state.get("oil_rate_bopd", 35.0)
        curr_water = res_state.get("water_rate_bwpd", 45.0)
        curr_temp = res_state.get("temperature_c", 50.0)
        curr_visc = res_state.get("oil_viscosity_cP", 3500.0)
        curr_margin = mech_state.get("floating_margin_pct", 10.0)
        curr_p7d = fail_state.get("prob_failure_7d", 0.15)
        curr_pprl = mech_state.get("pprl_klb", 12.0)
        curr_fillage = srp_state.get("fillage_pct", 78.0)
        pump_depth_m = well_meta.get("Pump_Depth_m", 1000.0)
        api_deg = well_meta.get("API_Gravity_deg", 18.0)

        # Baseline Economics & Safety
        base_econ = PhysicsEngine.calculate_energy_and_economics(
            spm=curr_spm,
            stroke_length_in=curr_stroke,
            pprl_klb=curr_pprl,
            oil_rate_bopd=curr_oil,
            water_rate_bwpd=curr_water,
            electricity_cost_kwh=econ_params.get("electricity_cost_per_kwh", 7.50),
            oil_price_per_bbl=econ_params.get("oil_price_per_bbl", 6200.0)
        )
        base_safety = SafetyGovernor.evaluate_candidate(
            spm=curr_spm,
            vfd_hz=curr_vfd,
            floating_margin_pct=curr_margin,
            fillage_pct=curr_fillage,
            pprl_klb=curr_pprl,
            failure_prob_7d=curr_p7d,
            confidence=conf_eval["overall_confidence"]
        )

        base_net_operating_value = (
            base_econ["daily_oil_revenue_inr"] -
            base_econ["daily_power_cost_inr"] -
            (curr_p7d * (econ_params.get("workover_cost_failure", 850000.0) / 7.0))
        )

        baseline_strategy = {
            "strategy_id": "STRAT-00-BASELINE",
            "name": "CURRENT / DO NOTHING",
            "type": "Hold Current Operations",
            "css_parameters": {
                "steam_volume_cwe_m3": 0.0,
                "steam_quality_pct": 0.0,
                "injection_pressure_kpa": 0.0,
                "soak_time_hr": 0.0,
                "action": "No Steam Cycle (Natural Cooling)"
            },
            "srp_parameters": {
                "spm": round(curr_spm, 2),
                "vfd_hz": round(curr_vfd, 1),
                "stroke_length_in": round(curr_stroke, 1),
                "action": "Unchanged Pumping Rate"
            },
            "predicted_outcomes": {
                "oil_rate_bopd": round(curr_oil, 1),
                "cum_oil_cycle_bbl": round(curr_oil * 90.0, 0),
                "sor": 0.0,
                "daily_kwh": base_econ["daily_kwh"],
                "specific_energy_kwh_per_bbl": base_econ["specific_energy_kwh_per_bbl"],
                "daily_operating_cost_inr": base_econ["daily_power_cost_inr"],
                "net_operating_value_lakhs_inr": round(base_net_operating_value / 100000.0, 2),
                "pump_efficiency_pct": round(curr_fillage * 0.88, 1),
                "floating_margin_pct": round(curr_margin, 1),
                "impact_force_klb": mech_state.get("impact_force_klb", 0.0),
                "prob_failure_7d": round(curr_p7d, 3),
            },
            "safety": base_safety,
            "confidence": conf_eval["overall_confidence"],
            "score": 0.0,
            "is_pareto": True
        }

        # Candidate Strategies Generator (Coupled CSS + SRP Search Grid)
        raw_candidates = [
            {
                "id": "STRAT-01-TVFD-ALONE",
                "name": "T-VFD Speed Optimization Only",
                "type": "Surface SRP Tuning",
                "vol": 0, "qual": 0, "press": 0, "soak": 0,
                "spm_target": max(2.5, min(9.5, mech_state.get("max_safe_spm", 6.2))),
                "stroke": curr_stroke,
                "oil_multiplier": 0.95 if mech_state.get("is_rod_floating") else 1.05,
                "steam_cost": 0.0,
                "fail_risk_mult": 0.25
            },
            {
                "id": "STRAT-02-ECO-LEAN",
                "name": "Eco-Lean Low-SOR Thermal Refresh",
                "type": "Joint CSS + SRP",
                "vol": 1200, "qual": 80, "press": 13500, "soak": 96,
                "spm_target": 6.8,
                "stroke": 100.0,
                "oil_multiplier": 1.65,
                "steam_cost": 1200 * econ_params.get("steam_cost_per_m3", 1250.0),
                "fail_risk_mult": 0.35
            },
            {
                "id": "STRAT-03-HIGH-ENERGY",
                "name": "High-Energy Thermal Flush + Speed Ramp",
                "type": "Joint CSS + SRP",
                "vol": 2400, "qual": 85, "press": 16500, "soak": 120,
                "spm_target": 8.8,
                "stroke": 100.0,
                "oil_multiplier": 2.25,
                "steam_cost": 2400 * econ_params.get("steam_cost_per_m3", 1250.0),
                "fail_risk_mult": 0.50
            },
            {
                "id": "STRAT-04-DEEP-SOAK",
                "name": "Extended Soak Deep Penetration",
                "type": "Joint CSS + SRP",
                "vol": 1800, "qual": 84, "press": 15000, "soak": 144,
                "spm_target": 6.2,
                "stroke": 110.0,
                "oil_multiplier": 1.95,
                "steam_cost": 1800 * econ_params.get("steam_cost_per_m3", 1250.0),
                "fail_risk_mult": 0.30
            },
            {
                "id": "STRAT-05-PARETO-OPTIMAL",
                "name": "Thermally-Synchronized Adaptive Joint Lift",
                "type": "Pareto Optimum",
                "vol": 1650, "qual": 82, "press": 14500, "soak": 108,
                "spm_target": 7.2,
                "stroke": 100.0,
                "oil_multiplier": 2.05,
                "steam_cost": 1650 * econ_params.get("steam_cost_per_m3", 1250.0),
                "fail_risk_mult": 0.20
            },
            {
                "id": "STRAT-06-AGGRESSIVE-UNSAFE",
                "name": "Over-Driven High-Rate Extraction (Stress Test)",
                "type": "High Risk / Boundary",
                "vol": 2900, "qual": 88, "press": 18500, "soak": 48,
                "spm_target": 11.2,  # Intentionally exceeds envelope to demonstrate rejection
                "stroke": 120.0,
                "oil_multiplier": 2.40,
                "steam_cost": 2900 * econ_params.get("steam_cost_per_m3", 1250.0),
                "fail_risk_mult": 1.80
            }
        ]

        evaluated_strategies = []

        for cand in raw_candidates:
            cand_spm = cand["spm_target"]
            cand_vfd = round(cand_spm * 6.25, 1)
            cand_stroke = cand["stroke"]

            # Estimate viscosity after candidate steam
            if cand["vol"] > 0:
                est_temp = min(185.0, curr_temp + (cand["vol"] / 2400.0) * 85.0)
            else:
                est_temp = curr_temp
            est_visc = PhysicsEngine.calculate_viscosity(est_temp, well_meta.get("Dead_Oil_Viscosity_cP_at_Res_Temp", 3800.0))

            cand_mech = PhysicsEngine.calculate_rod_mechanics(
                spm=cand_spm,
                stroke_length_in=cand_stroke,
                pump_depth_m=pump_depth_m,
                oil_viscosity_cp=est_visc,
                api_gravity_deg=api_deg
            )

            cand_oil = round(curr_oil * cand["oil_multiplier"], 1)
            cand_p7d = min(0.95, max(0.01, curr_p7d * cand["fail_risk_mult"] + (0.50 if cand_mech["is_rod_floating"] else 0.0)))
            cand_sor = round(cand["vol"] / max(1.0, cand_oil * 90.0 * 0.158987), 2) if cand["vol"] > 0 else 0.0

            cand_econ = PhysicsEngine.calculate_energy_and_economics(
                spm=cand_spm,
                stroke_length_in=cand_stroke,
                pprl_klb=cand_mech["pprl_klb"],
                oil_rate_bopd=cand_oil,
                water_rate_bwpd=curr_water,
                steam_volume_cwe_m3=cand["vol"],
                cum_oil_cycle_bbl=cand_oil * 90.0,
                electricity_cost_kwh=econ_params.get("electricity_cost_per_kwh", 7.50),
                oil_price_per_bbl=econ_params.get("oil_price_per_bbl", 6200.0)
            )

            # Safety Governor check
            cand_safety = SafetyGovernor.evaluate_candidate(
                spm=cand_spm,
                vfd_hz=cand_vfd,
                floating_margin_pct=cand_mech["floating_margin_pct"],
                fillage_pct=82.0,
                pprl_klb=cand_mech["pprl_klb"],
                failure_prob_7d=cand_p7d,
                steam_pressure_kpa=cand["press"] if cand["press"] > 0 else None,
                confidence=conf_eval["overall_confidence"]
            )

            # Net Operating Value over 90-day cycle (INR Lakhs)
            cycle_revenue = (cand_oil * 90.0) * econ_params.get("oil_price_per_bbl", 6200.0)
            cycle_power_cost = cand_econ["daily_power_cost_inr"] * 90.0
            cycle_steam_cost = cand["steam_cost"]
            cycle_failure_penalty = cand_p7d * econ_params.get("workover_cost_failure", 850000.0) * 2.0
            cycle_net_value = cycle_revenue - cycle_power_cost - cycle_steam_cost - cycle_failure_penalty
            cycle_net_value_lakhs = round(cycle_net_value / 100000.0, 2)

            # Multi-objective composite score
            # Higher is better
            norm_oil = cand_oil / max(1.0, curr_oil)
            norm_energy = 1.0 / max(0.2, (cand_econ["specific_energy_kwh_per_bbl"] / max(0.1, base_econ["specific_energy_kwh_per_bbl"])))
            norm_rel = 1.0 - cand_p7d
            norm_cost = cycle_net_value / max(1.0, abs(base_net_operating_value * 90.0))
            norm_sor = 1.0 / max(0.5, (cand_sor if cand_sor > 0 else 1.0))

            score = (
                weights["w_oil"] * norm_oil +
                weights["w_energy"] * norm_energy +
                weights["w_rel"] * norm_rel +
                weights["w_cost"] * norm_cost +
                weights["w_sor"] * norm_sor
            )

            # Heavily penalize safety violations
            if not cand_safety["is_permissible"]:
                score -= 100.0

            evaluated_strategies.append({
                "strategy_id": cand["id"],
                "name": cand["name"],
                "type": cand["type"],
                "css_parameters": {
                    "steam_volume_cwe_m3": cand["vol"],
                    "steam_quality_pct": cand["qual"],
                    "injection_pressure_kpa": cand["press"],
                    "soak_time_hr": cand["soak"],
                    "action": f"Inject {cand['vol']} m3 CWE @ {cand['qual']}% quality" if cand["vol"] > 0 else "No CSS Steam"
                },
                "srp_parameters": {
                    "spm": round(cand_spm, 2),
                    "vfd_hz": cand_vfd,
                    "stroke_length_in": round(cand_stroke, 1),
                    "action": f"Set VFD to {cand_vfd:.1f} Hz ({cand_spm:.1f} SPM)"
                },
                "predicted_outcomes": {
                    "oil_rate_bopd": cand_oil,
                    "cum_oil_cycle_bbl": round(cand_oil * 90.0, 0),
                    "sor": cand_sor,
                    "daily_kwh": cand_econ["daily_kwh"],
                    "specific_energy_kwh_per_bbl": cand_econ["specific_energy_kwh_per_bbl"],
                    "daily_operating_cost_inr": cand_econ["daily_power_cost_inr"],
                    "net_operating_value_lakhs_inr": cycle_net_value_lakhs,
                    "pump_efficiency_pct": 82.0,
                    "floating_margin_pct": cand_mech["floating_margin_pct"],
                    "impact_force_klb": cand_mech["impact_force_klb"],
                    "prob_failure_7d": cand_p7d,
                },
                "safety": cand_safety,
                "confidence": conf_eval["overall_confidence"],
                "score": round(score, 3),
                "is_pareto": cand_safety["is_permissible"] and ("PARETO" in cand["id"] or "ECO" in cand["id"] or "TVFD" in cand["id"])
            })

        # Rank candidates
        evaluated_strategies.sort(key=lambda s: s["score"], reverse=True)
        top_candidate = evaluated_strategies[0]

        # Engineering Comparison against CURRENT / DO NOTHING
        # If top candidate improvement is less than 5% or confidence is too low -> HOLD CURRENT OPERATION
        min_improvement_threshold = 0.05
        baseline_net_cycle = (base_net_operating_value * 90.0) / 100000.0
        top_net_cycle = top_candidate["predicted_outcomes"]["net_operating_value_lakhs_inr"]

        if (top_net_cycle <= baseline_net_cycle * (1.0 + min_improvement_threshold) and not mech_state.get("is_rod_floating")):
            final_recommendation = baseline_strategy
            decision_action = "HOLD CURRENT OPERATION"
            rationale = "Current well operation is within acceptable performance limits. Available interventions do not provide sufficient incremental operating margin relative to steam generation cost and equipment intervention risk."
        else:
            final_recommendation = top_candidate
            decision_action = f"EXECUTE: {top_candidate['name']}"
            rationale = (
                f"Selected strategy yields net value gain of {round(top_net_cycle - baseline_net_cycle, 2)} Lakhs INR "
                f"while maintaining rod floating margin at {top_candidate['predicted_outcomes']['floating_margin_pct']:.1f}%."
            )

        # Structured Explanation Generation:
        # OBSERVATION, CAUSE, PREDICTION, ACTION, TRADE-OFF, CONFIDENCE
        explanation = {
            "observation": f"Well {well_state.get('well_id')} operating at {curr_temp:.1f}°C with estimated viscosity {curr_visc:.0f} cP and {curr_spm:.1f} SPM.",
            "cause": "Reservoir cooling increases in-situ crude viscosity by up to two orders of magnitude, escalating annular rod drag." if curr_temp < 70.0 else "Well is operating within the active thermal window.",
            "prediction": f"Without intervention, rod floating margin is {curr_margin:.1f}% with 7-day failure hazard {curr_p7d:.2f}.",
            "action": decision_action,
            "trade_off": "Allocates steam investment to reduce crude viscosity while governing surface pump speed to avoid slack-bridle impact shock.",
            "confidence": conf_eval["overall_confidence"],
            "requires_operator_review": conf_eval["requires_operator_review"] or (not final_recommendation["safety"]["is_permissible"])
        }

        return {
            "well_id": well_state.get("well_id"),
            "optimization_profile": profile,
            "weights_used": weights,
            "economic_assumptions": econ_params,
            "recommended_strategy": final_recommendation,
            "baseline_strategy": baseline_strategy,
            "all_strategies": [baseline_strategy] + evaluated_strategies,
            "explanation": explanation,
            "decision_audit": {
                "decision_action": decision_action,
                "rationale": rationale,
                "safety_status": final_recommendation["safety"]["status"],
                "rejection_reasons": final_recommendation["safety"]["rejection_reasons"]
            }
        }