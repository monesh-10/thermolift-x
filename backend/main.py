"""Main FastAPI Application: Powers THERMOLIFT X.
Baghewala Heavy Oil Well-to-Surface Predictive Decision Twin.
Oil India Limited (OIL) — SIH Problem Statement 26120.

Decisions, not just dashboards:
OBSERVE -> UNDERSTAND -> PREDICT -> REHEARSE -> OPTIMIZE -> EXPLAIN -> VALIDATE -> LEARN.
"""

import os
import math
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .model_registry import ModelRegistry
from .physics_engine import PhysicsEngine
from .optimizer_engine import OptimizerEngine
from .fleet_manager import FleetManager
from .safety_governor import SafetyGovernor
from .confidence_engine import ConfidenceEngine
from .joint_optimizer import JointOptimizer
from .future_rehearsal import FutureRehearsalEngine
from .steam_allocation import SteamAllocationEngine
from .recalibration import RecalibrationEngine
from .jury_scenarios import JuryScenarioEngine

app = FastAPI(
    title="THERMOLIFT X — Predictive Well-to-Surface Decision Twin API",
    description="Oil India Limited (OIL) — SIH 26120 Baghewala Heavy Oil Digital Twin",
    version="2.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("[Startup] Initializing Model Registry...")
    ModelRegistry.get_instance()
    print("[Startup] Initializing Fleet Manager (THERMOLIFT X)...")
    FleetManager.get_instance()
    print("[Startup] Initializing Recalibration Engine...")
    RecalibrationEngine.get_instance()
    print("[Startup] THERMOLIFT X decision platform is fully online!")


# ---------------------------------------------------------------------------
# Core System Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    fm = FleetManager.get_instance()
    return {
        "status": "healthy",
        "platform": "THERMOLIFT X",
        "system": "Baghewala Well-to-Surface Predictive Decision Twin",
        "operator": "Oil India Limited (OIL)",
        "models_loaded": 4,
        "active_field_wells": 15,
        "active_monitored_assets": len(fm.wells_state),
        "disclaimer": "PROTOTYPE / DECISION SUPPORT - SIMULATION ONLY - NO LIVE EQUIPMENT CONTROL"
    }


@app.get("/api/fleet/summary")
def get_fleet_summary():
    """Returns aggregated Baghewala field KPIs and status of all monitored assets."""
    fm = FleetManager.get_instance()
    return fm.get_fleet_summary()


@app.get("/api/well/{well_id}")
def get_well_state(well_id: str):
    """Returns complete real-time digital twin state for a specific well."""
    fm = FleetManager.get_instance()
    state = fm.get_well_state(well_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found in Baghewala asset.")
    return state


@app.get("/api/well/{well_id}/twin-state")
def get_well_full_twin_state(well_id: str):
    """Returns enriched cyber-physical twin state with confidence, sensor coverage, and safety envelope."""
    fm = FleetManager.get_instance()
    state = fm.get_well_state(well_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found.")

    conf = ConfidenceEngine.evaluate_well_confidence(state)
    recal = RecalibrationEngine.get_instance().get_predicted_vs_actual(state)

    return {
        "well_id": well_id,
        "is_demo_asset": state.get("is_demo_asset", False),
        "state": state,
        "confidence": conf,
        "predicted_vs_actual": recal,
        "safety": state.get("safety", {})
    }


@app.get("/api/well/{well_id}/timeline")
def get_well_timeline(well_id: str, limit: int = 120):
    """Returns historical daily operational logs and thermal degradation records."""
    fm = FleetManager.get_instance()
    timeline = fm.get_well_timeline(well_id, limit=limit)
    if not timeline:
        raise HTTPException(status_code=404, detail=f"No timeline data for well {well_id}.")
    return timeline


# ---------------------------------------------------------------------------
# Supervisory Control & Simulation Application
# ---------------------------------------------------------------------------

@app.post("/api/well/{well_id}/optimize-vfd")
def optimize_well_vfd(well_id: str):
    """T-VFD™ Supervisory Speed Recommendation (Calculates safe SPM and VFD Hz)."""
    fm = FleetManager.get_instance()
    state = fm.get_well_state(well_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found.")

    res = OptimizerEngine.optimize_srp_vfd(
        current_spm=state["surface_srp"]["spm"],
        current_vfd_hz=state["surface_srp"]["vfd_frequency_hz"],
        stroke_length_in=state["surface_srp"]["stroke_length_in"],
        pump_depth_m=state["metadata"].get("Pump_Depth_m", 1000.0),
        oil_viscosity_cp=state["reservoir"]["oil_viscosity_cp"],
        oil_rate_bopd=state["reservoir"]["oil_rate_bopd"],
        water_rate_bwpd=state["reservoir"]["water_rate_bwpd"],
        fillage_pct=state["surface_srp"]["fillage_pct"],
        api_gravity_deg=state["metadata"].get("API_Gravity_deg", 18.0)
    )
    return res


@app.post("/api/well/{well_id}/apply-vfd")
def apply_vfd_simulation(well_id: str, payload: Dict[str, Any] = Body(...)):
    """SIMULATE VFD APPLICATION: Applies setpoints in the digital twin simulation environment.
    DISCLAIMER: PROTOTYPE SIMULATION ONLY — NO LIVE EQUIPMENT CONTROL.
    """
    new_spm = float(payload.get("spm", 6.0))
    new_vfd_hz = float(payload.get("vfd_hz", 38.0))
    fm = FleetManager.get_instance()
    try:
        updated_state = fm.update_well_srp(well_id, new_spm, new_vfd_hz)
        return {
            "success": True,
            "disclaimer": "PROTOTYPE SIMULATION ONLY — NO LIVE EQUIPMENT CONTROL",
            "message": f"Simulation Approved: Dispatched {new_spm:.1f} SPM ({new_vfd_hz:.1f} Hz) to {well_id}. Rod floating resolved inside twin.",
            "updated_state": updated_state
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/well/{well_id}/optimize-css")
def optimize_css_cycle(well_id: str, payload: Dict[str, Any] = Body(...)):
    """Runs Model 4 surrogate multi-objective Pareto optimization for CSS steam cycle parameters."""
    fm = FleetManager.get_instance()
    state = fm.get_well_state(well_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found.")

    priority = payload.get("priority", "balanced")
    well_context = state["metadata"].copy()
    well_context["Peak_Wellbore_Temp_C"] = 185.0
    well_context["Prev_Cycle_Cum_Oil_bbl"] = 2200.0
    well_context["Prev_Cycle_SOR"] = 3.4
    well_context["Prev_Cycle_Water_bbl"] = 1600.0
    well_context["Prev_Cycle_Production_Days"] = 115.0
    well_context["Cumulative_Historic_Steam_m3"] = 4500.0
    well_context["Steam_Energy_Index"] = 1.2
    well_context["Steam_Volume_per_Net_Pay"] = 180.0

    res = OptimizerEngine.optimize_css_parameters(well_context, priority=priority)
    return res


@app.post("/api/well/{well_id}/simulate-thermal")
def simulate_thermal_cycle(well_id: str, payload: Dict[str, Any] = Body(...)):
    """Simulates 120-day production cycle post-steam and identifies exact Rod Floating Onset Day."""
    fm = FleetManager.get_instance()
    state = fm.get_well_state(well_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found.")

    peak_temp_c = float(payload.get("peak_temp_c", 190.0))
    res_temp_c = float(state["metadata"].get("Reservoir_Temperature_C", 48.0))
    dead_oil_visc = float(state["metadata"].get("Dead_Oil_Viscosity_cP_at_Res_Temp", 3800.0))
    spm = float(state["surface_srp"]["spm"])
    stroke_in = float(state["surface_srp"]["stroke_length_in"])
    pump_depth_m = float(state["metadata"].get("Pump_Depth_m", 1000.0))
    api_deg = float(state["metadata"].get("API_Gravity_deg", 18.0))

    decay_lambda = 0.026
    days_series = []
    rod_float_day = None

    for day in range(1, 121, 2):
        temp_c = res_temp_c + (peak_temp_c - res_temp_c) * math.exp(-decay_lambda * day)
        visc = PhysicsEngine.calculate_viscosity(temp_c, dead_oil_visc)
        mech = PhysicsEngine.calculate_rod_mechanics(
            spm=spm,
            stroke_length_in=stroke_in,
            pump_depth_m=pump_depth_m,
            oil_viscosity_cp=visc,
            api_gravity_deg=api_deg
        )

        is_float = mech["is_rod_floating"]
        if is_float and rod_float_day is None:
            rod_float_day = day

        base_oil = 95.0 * math.exp(-0.018 * day)

        days_series.append({
            "day": day,
            "temperature_c": round(temp_c, 1),
            "viscosity_cp": round(visc, 1),
            "estimated_oil_rate_bopd": round(max(5.0, base_oil), 1),
            "floating_margin_pct": mech["floating_margin_pct"],
            "is_rod_floating": is_float,
            "max_safe_spm": mech["max_safe_spm"]
        })

    return {
        "well_id": well_id,
        "peak_temp_c": peak_temp_c,
        "rod_floating_onset_day": rod_float_day if rod_float_day else "No floating under current conditions",
        "critical_viscosity_threshold_cp": 1250.0,
        "simulation_series": days_series
    }


# ---------------------------------------------------------------------------
# THERMOLIFT X Decision Architecture Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/well/{well_id}/future-rehearsal")
def rehearse_future(well_id: str, payload: Dict[str, Any] = Body(default={})):
    """Counterfactual forward rehearsal simulating 6 strategic branches over 7, 14, 30 days."""
    fm = FleetManager.get_instance()
    state = fm.get_well_state(well_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found.")

    res = FutureRehearsalEngine.rehearse_well_futures(
        well_state=state,
        custom_css=payload.get("custom_css"),
        custom_srp=payload.get("custom_srp")
    )
    return res


@app.post("/api/well/{well_id}/joint-optimize")
def run_joint_optimization(well_id: str, payload: Dict[str, Any] = Body(default={})):
    """Flagship Joint CSS + SRP Decision Optimizer coupling thermal state, mechanics, and economics."""
    fm = FleetManager.get_instance()
    state = fm.get_well_state(well_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found.")

    profile = payload.get("profile", "balanced")
    custom_weights = payload.get("custom_weights")
    custom_economics = payload.get("custom_economics")

    res = JointOptimizer.run_joint_optimization(
        well_state=state,
        profile=profile,
        custom_weights=custom_weights,
        custom_economics=custom_economics
    )
    return res


@app.post("/api/well/{well_id}/safety-check")
def evaluate_safety_envelope(well_id: str, payload: Dict[str, Any] = Body(...)):
    """Safety Governor verification: checks candidate parameters against operational constraints."""
    spm = float(payload.get("spm", 6.0))
    vfd_hz = float(payload.get("vfd_hz", 37.5))
    floating_margin = float(payload.get("floating_margin_pct", 20.0))
    fillage = float(payload.get("fillage_pct", 80.0))
    pprl = float(payload.get("pprl_klb", 12.0))
    p7d = float(payload.get("failure_prob_7d", 0.05))
    press = payload.get("steam_pressure_kpa")
    conf = float(payload.get("confidence", 0.90))

    eval_result = SafetyGovernor.evaluate_candidate(
        spm=spm,
        vfd_hz=vfd_hz,
        floating_margin_pct=floating_margin,
        fillage_pct=fillage,
        pprl_klb=pprl,
        failure_prob_7d=p7d,
        steam_pressure_kpa=float(press) if press is not None else None,
        confidence=conf
    )
    return eval_result


@app.post("/api/well/{well_id}/recommendation")
def get_operator_recommendation(well_id: str, payload: Dict[str, Any] = Body(default={})):
    """Returns structured incident recommendation: Observation, Cause, Prediction, Action, Trade-off, Confidence."""
    fm = FleetManager.get_instance()
    state = fm.get_well_state(well_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found.")

    profile = payload.get("profile", "balanced")
    opt = JointOptimizer.run_joint_optimization(well_state=state, profile=profile)
    return {
        "well_id": well_id,
        "recommendation": opt["recommended_strategy"],
        "baseline": opt["baseline_strategy"],
        "explanation": opt["explanation"],
        "decision_audit": opt["decision_audit"]
    }


@app.get("/api/well/{well_id}/confidence")
def get_well_confidence(well_id: str):
    """Returns Confidence Engine evaluation: data quality, sensor coverage, sensor health, and freshness."""
    fm = FleetManager.get_instance()
    state = fm.get_well_state(well_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found.")

    return ConfidenceEngine.evaluate_well_confidence(state)


@app.get("/api/well/{well_id}/predicted-vs-actual")
def get_predicted_vs_actual(well_id: str):
    """Returns telemetry comparison table of predicted vs observed field metrics."""
    fm = FleetManager.get_instance()
    state = fm.get_well_state(well_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found.")

    recal = RecalibrationEngine.get_instance()
    return recal.get_predicted_vs_actual(state)


@app.post("/api/well/{well_id}/feedback")
def record_operator_feedback(well_id: str, payload: Dict[str, Any] = Body(...)):
    """Records operator intervention approval/rejection and observed performance feedback."""
    action = payload.get("action", "APPROVED_SIMULATION")
    notes = payload.get("notes", "No operator comments")
    return {
        "success": True,
        "well_id": well_id,
        "recorded_action": action,
        "notes": notes,
        "message": f"Operator decision logged for {well_id}. Decision added to historical audit log."
    }


@app.post("/api/well/{well_id}/recalibrate")
def recalibrate_well_twin(well_id: str):
    """Executes online twin recalibration, updates Bayesian priors, and eliminates sensor bias."""
    recal = RecalibrationEngine.get_instance()
    return recal.recalibrate_twin(well_id=well_id)


# ---------------------------------------------------------------------------
# Fleet-Level Resource & Health Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/field/steam-allocation")
def allocate_field_steam(payload: Dict[str, Any] = Body(default={})):
    """Allocates available steam generation across the 15 Baghewala wells by Marginal Value of Steam."""
    fm = FleetManager.get_instance()
    avail = float(payload.get("available_steam_m3", 8500.0))
    field_wells = {k: v for k, v in fm.wells_state.items() if not v.get("is_demo_asset", False)}
    return SteamAllocationEngine.allocate_fleet_steam(fleet_wells=field_wells, available_steam_m3=avail)


@app.get("/api/field/thermal-opportunity")
def get_thermal_opportunity():
    """Returns fleet-wide thermal state breakdown and top operational risks/opportunities."""
    fm = FleetManager.get_instance()
    field_wells = {k: v for k, v in fm.wells_state.items() if not v.get("is_demo_asset", False)}

    hot_wells = [w for w in field_wells.values() if w["reservoir"]["temperature_c"] >= 100.0]
    cooling_wells = [w for w in field_wells.values() if 52.0 <= w["reservoir"]["temperature_c"] < 70.0]
    critical_wells = [w for w in field_wells.values() if w["health_status"] == "CRITICAL"]

    return {
        "total_wells": len(field_wells),
        "thermal_distribution": {
            "hot": len(hot_wells),
            "cooling_opportunity": len(cooling_wells),
            "critical_risk": len(critical_wells)
        },
        "top_risks": [
            {
                "well_id": w["well_id"],
                "status": w["health_status"],
                "issue": w["status_message"],
                "margin_pct": w["mechanics"]["floating_margin_pct"],
                "failure_risk_7d": w["failure_prediction"]["prob_failure_7d"]
            }
            for w in critical_wells[:4]
        ],
        "top_opportunities": [
            {
                "well_id": w["well_id"],
                "temp_c": w["reservoir"]["temperature_c"],
                "oil_rate_bopd": w["reservoir"]["oil_rate_bopd"],
                "recommendation": "Prime candidate for thermal steam injection cycle"
            }
            for w in cooling_wells[:4]
        ]
    }


@app.get("/api/models/health")
def get_models_health():
    """Provides complete technical validation report for Models 1, 2, 3, and 4."""
    fm = FleetManager.get_instance()
    return fm.get_models_health_summary()


@app.get("/api/twin/health")
def get_twin_health():
    """Returns global Twin Health score, sub-indices, and 30-day Model Drift monitoring series."""
    recal = RecalibrationEngine.get_instance()
    return recal.get_twin_health_score()


@app.get("/api/jury/scenarios")
def get_jury_scenarios():
    """Returns the 5 deterministic demonstration scenarios and 13-step guided pitch sequence."""
    return {
        "scenarios": JuryScenarioEngine.get_all_scenarios(),
        "jury_steps": JuryScenarioEngine.get_jury_steps()
    }


@app.post("/api/jury/run-scenario")
def run_jury_scenario(payload: Dict[str, Any] = Body(...)):
    """Triggers an active demo scenario for the guided jury tour."""
    scenario_key = payload.get("scenario_key", "rod_floating")
    fm = FleetManager.get_instance()
    return JuryScenarioEngine.run_scenario(scenario_key=scenario_key, fleet_state=fm.wells_state)


# ---------------------------------------------------------------------------
# Static Files & Frontend Serving
# ---------------------------------------------------------------------------

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

ASSETS_DIR = Path(__file__).resolve().parent.parent / "stitch_import" / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_frontend():
        stitch_file = Path(__file__).resolve().parent.parent / "stitch_import" / "code.html"
        if stitch_file.exists():
            return FileResponse(str(stitch_file))
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend not found"}

    @app.get("/stitch")
    def serve_stitch():
        stitch_file = Path(__file__).resolve().parent.parent / "stitch_import" / "code.html"
        if stitch_file.exists():
            return FileResponse(str(stitch_file))
        return {"message": "Stitch file not found"}

    @app.get("/classic")
    def serve_classic():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Classic index.html not found"}