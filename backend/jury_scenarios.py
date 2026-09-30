"""Jury Scenarios & Operational Incident Walkthrough Engine.
Professional engineering walkthrough of the closed-loop decision workflow:
1. 5 Deterministic Scenarios (Healthy Well, Thermal Cooling, High Stress, Rod Floating, Constrained Steam).
2. Synthetic Demo Asset BGW-017 (Clearly labeled: DEMO ASSET).
3. 13-Step Automated Case Incident Walkthrough for evaluation.
"""

from typing import Dict, Any, List, Optional


class JuryScenarioEngine:
    SCENARIOS = {
        "healthy_well": {
            "id": "SCENARIO_1_HEALTHY",
            "name": "Scenario 1: Stable Operating Well (BGW-001)",
            "well_id": "BGW-001",
            "description": "Post-steam early cycle with warm temperature (115°C), low crude viscosity (140 cP), safe rod fall margin (+42%), and low failure risk.",
            "operational_state": "HEALTHY",
            "narrative": "Stable operational regime. Thermal monitoring active to anticipate future viscosity surge."
        },
        "cooling_reservoir": {
            "id": "SCENARIO_2_COOLING",
            "name": "Scenario 2: Thermal Cooling & Viscosity Surge (BGW-003)",
            "well_id": "BGW-003",
            "description": "Late production cycle: Reservoir cooled to 54°C, viscosity escalated to 3,200 cP. Falling margin is down to +11% (AMBER).",
            "operational_state": "WARNING",
            "narrative": "Late-cycle thermal cooling increases annular shear. Digital twin forecasts impending rod float threshold."
        },
        "high_loading": {
            "id": "SCENARIO_3_HIGH_STRESS",
            "name": "Scenario 3: High Rod String Stress & Friction (BGW-005)",
            "well_id": "BGW-005",
            "description": "Deep completion (1,120 m TVD) producing 17.1° API heavy crude. Annular viscous drag drives PPRL to 19.8 klb near rod yield boundary.",
            "operational_state": "WARNING",
            "narrative": "Stress-constrained regime. Safety governor limits maximum SPM to protect rod string tensile limits."
        },
        "rod_floating": {
            "id": "SCENARIO_4_ROD_FLOATING",
            "name": "Scenario 4: Severe Rod Floating & Impact Shock (BGW-002)",
            "well_id": "BGW-002",
            "description": "CRITICAL ANOMALY: Sucker rod falls slower than polished rod (Margin -18.5%). Carrier bar separates, creating slack bridle and 4.8 klb impact shock.",
            "operational_state": "CRITICAL",
            "narrative": "Severe annular drag triggers carrier separation and cyclic shock loads. T-VFD prescribes speed throttling."
        },
        "limited_steam": {
            "id": "SCENARIO_5_LIMITED_STEAM",
            "name": "Scenario 5: Constrained Field Steam Allocation (Fleet-Wide)",
            "well_id": "ALL_15_WELLS",
            "description": "Field boiler generation limited to 8,500 m³ CWE across 15 wells. Evaluates Marginal Value of Steam to rank and prioritize allocation.",
            "operational_state": "FLEET_ALLOCATION",
            "narrative": "Fleet-wide knapsack optimization distributing boiler capacity to wells with highest marginal oil return."
        },
        "demo_well_17": {
            "id": "SCENARIO_6_DEMO_17",
            "name": "Demonstration Asset (BGW-017 DEMO)",
            "well_id": "BGW-017",
            "description": "Dedicated synthetic demonstration scenario showing end-to-end 13-step decision workflow under controlled boundary conditions.",
            "operational_state": "CRITICAL",
            "narrative": "Synthetic demonstration asset for end-to-end evaluation: from thermal cooling to future rehearsal, joint optimization, and recalibration."
        }
    }

    JURY_STEPS = [
        {
            "step": 1,
            "title": "Field Production Overview",
            "key_question": "BASELINE FIELD STATUS & DISCONNECTED OPERATIONS",
            "narrative_statement": "In the Baghewala heavy oil asset (Jodhpur Sandstone), Cyclic Steam Stimulation (CSS) and Sucker Rod Pump (SRP) artificial lift operations have historically been planned independently. Post-steam cooling from ~190°C down to 48°C triggers a two-orders-of-magnitude surge in viscosity.",
            "action_trigger": "show_field_command_center",
            "target_view": "command_center",
            "key_data_points": ["15 Field Wells", "17–19° API Heavy Crude", "Viscosity Surge: 35 cP to 5,000+ cP"]
        },
        {
            "step": 2,
            "title": "Incident Detection on Well BGW-002",
            "key_question": "THERMAL COOLING & KINEMATIC ANOMALY",
            "narrative_statement": "Well BGW-002 has entered late-cycle cooling (wellbore temp down to 52.0°C, crude viscosity surging to 3,600 cP). Polished rod descent speed at 8.5 SPM exceeds the terminal sinking velocity of the rod string in cold heavy crude.",
            "action_trigger": "select_well_bgw002",
            "target_view": "well_intelligence",
            "key_data_points": ["Wellbore Temp: 52.0°C", "In-Situ Viscosity: 3,600 cP", "Floating Margin: -18.5% (NEGATIVE)"]
        },
        {
            "step": 3,
            "title": "Digital Twin Kinematics & Slack Bridle",
            "key_question": "MECHANICAL FAILURE MECHANISM",
            "narrative_statement": "Stokes-Navier annular viscous drag exceeds buoyant rod string weight. The carrier bar separates from the rod clamp on the downstroke, creating slack bridle and a severe 4.8 klb impact shock on upstroke turnaround, escalating parting risk.",
            "action_trigger": "open_digital_twin_rig",
            "target_view": "digital_twin",
            "key_data_points": ["Carrier Bar Separation Visible", "Impact Shock Load: 4.8 klb", "7-Day Failure Risk: 85%"]
        },
        {
            "step": 4,
            "title": "Surface Dynamometer Card Diagnosis",
            "key_question": "SURFACE DYNAMOMETER PATTERN",
            "narrative_statement": "Model 2 (Multiclass XGBoost) diagnoses the dynamometer card with 99.4% confidence as 'Fluid Pound / Rod Floating'. Downstroke polished rod load drops toward zero, followed by a sharp impact spike at the lower turnaround.",
            "action_trigger": "open_dyno_intelligence",
            "target_view": "dyno_intelligence",
            "key_data_points": ["Diagnosis: Fluid Pound / Rod Floating", "Model Confidence: 99.4%", "Hysteresis Distortion"]
        },
        {
            "step": 5,
            "title": "Counterfactual Forward Rehearsal",
            "key_question": "FORWARD MULTI-SCENARIO PROJECTION",
            "narrative_statement": "Before altering field equipment, the digital twin simulates 6 parallel forward branches across 7, 14, and 30-day horizons: evaluating Do Nothing, More Steam, Longer Soak, Surface T-VFD Speed Adjustment, Combined Action, and Joint Pareto Optimum.",
            "action_trigger": "run_future_rehearsal",
            "target_view": "future_rehearsal",
            "key_data_points": ["6 Parallel Branches", "30-Day Horizons", "Thermal & Mechanical Projections"]
        },
        {
            "step": 6,
            "title": "Joint CSS + SRP Decision Optimization",
            "key_question": "COUPLED THERMODYNAMIC & LIFT OPTIMIZATION",
            "narrative_statement": "The Joint Optimizer searches candidate strategies across steam injection volume, quality, pressure, soak duration, and surface VFD speed schedules, balancing incremental production against steam generation costs, power consumption, and equipment fatigue.",
            "action_trigger": "run_joint_optimization",
            "target_view": "joint_optimizer",
            "key_data_points": ["Coupled Decision Search", "Multi-Objective Weights", "Pareto Frontier Evaluated"]
        },
        {
            "step": 7,
            "title": "Prescriptive Engineering Recommendation",
            "key_question": "RECOMMENDED INTERVENTION",
            "narrative_statement": "The twin recommends a synchronized thermal pulse (1,650 m³ CWE @ 82% quality) coupled with immediate VFD speed throttling to 38.5 Hz (6.2 SPM). This eliminates rod floating while sustaining high lift recovery.",
            "action_trigger": "show_recommendation",
            "target_view": "decision_center",
            "key_data_points": ["Target SPM: 6.2 (38.5 Hz)", "Steam Pulse: 1,650 m³ CWE", "Incremental Oil: +1,850 bbl"]
        },
        {
            "step": 8,
            "title": "Safety Governor Envelope Verification",
            "key_question": "ENGINEERING CONSTRAINT COMPLIANCE",
            "narrative_statement": "The Safety Governor checks all 8 operational constraints. Pumping speed, VFD frequency, rod floating margin (+19.2%), peak load (12.4 klb vs 22.0 klb yield), and formation fracture pressure limits all pass verification.",
            "action_trigger": "inspect_safety_governor",
            "target_view": "decision_center",
            "key_data_points": ["Safety Status: PASSED", "Margin: +19.2% (Positive)", "Fracture Margin: Safe"]
        },
        {
            "step": 9,
            "title": "Uncertainty & Sensor Coverage Verification",
            "key_question": "DATA QUALITY & MODEL CONFIDENCE",
            "narrative_statement": "Every prediction carries uncertainty bounds. With 7 active wellhead telemetry streams, sensor coverage is 100% and confidence is 0.91. If telemetry degrades, the system automatically flags 'OPERATOR REVIEW REQUIRED'.",
            "action_trigger": "inspect_confidence_engine",
            "target_view": "decision_center",
            "key_data_points": ["Decision Confidence: 0.91", "Data Quality: 96%", "Active Sensors: 7/7"]
        },
        {
            "step": 10,
            "title": "Simulate Closed-Loop Setpoint Dispatch",
            "key_question": "SUPERVISORY SIMULATION DISPATCH",
            "narrative_statement": "The operator approves the simulation dispatch. Pumping speed slows to 6.2 SPM, restoring positive rod string descent. Carrier bar separation disappears on the kinematics canvas and the dyno card returns to a full pump pattern.",
            "action_trigger": "approve_simulation_dispatch",
            "target_view": "digital_twin",
            "key_data_points": ["Rod Floating Resolved", "Shock Force: 0.0 klb", "7-Day Failure Risk drops to 1.5%"]
        },
        {
            "step": 11,
            "title": "Predicted vs Actual Telemetry Comparison",
            "key_question": "POST-DISPATCH MODEL RESIDUALS",
            "narrative_statement": "Observed post-action field telemetry is compared with twin forecasts. Across oil rate, wellbore temperature, viscosity, and peak rod load, the mean absolute percentage error is 3.8%, well within the 7.0% engineering tolerance.",
            "action_trigger": "open_predicted_vs_actual",
            "target_view": "recalibration",
            "key_data_points": ["Mean Prediction Error: 3.8%", "Oil Rate Error: 4.1%", "Temp Error: 1.5%"]
        },
        {
            "step": 12,
            "title": "Online Recalibration & Twin Health",
            "key_question": "BAYESIAN RECALIBRATION & DRIFT AUDIT",
            "narrative_statement": "Clicking Recalibrate Twin updates online Bayesian prior distributions, removes sensor bias offsets, and verifies that rolling 30-day residuals remain stationary, maintaining Twin Health at an optimal 92.8%.",
            "action_trigger": "recalibrate_twin_step",
            "target_view": "recalibration",
            "key_data_points": ["Twin Health: 92.8%", "Stationary Residuals", "Priors Updated"]
        },
        {
            "step": 13,
            "title": "Field-Level Steam Allocation (Knapsack MVS)",
            "key_question": "FLEET BOILER CAPACITY ALLOCATION",
            "narrative_statement": "At the asset level, 8,500 m³ of boiler capacity is allocated across the 15 wells based on Marginal Value of Steam. Priority is given to cooling-window wells with high incremental oil yield, while still-hot wells are deferred.",
            "action_trigger": "open_field_steam",
            "target_view": "field_steam",
            "key_data_points": ["Allocated: 8,500 m³ CWE", "Average Fleet SOR: 4.12", "Net Incremental Oil: +6,420 bbl"]
        }
    ]

    @classmethod
    def get_all_scenarios(cls) -> Dict[str, Any]:
        return cls.SCENARIOS

    @classmethod
    def get_jury_steps(cls) -> List[Dict[str, Any]]:
        return cls.JURY_STEPS

    @classmethod
    def run_scenario(cls, scenario_key: str, fleet_state: Dict[str, Any]) -> Dict[str, Any]:
        scenario = cls.SCENARIOS.get(scenario_key, cls.SCENARIOS["rod_floating"])
        return {
            "scenario": scenario,
            "recommended_focus_well": scenario["well_id"],
            "instruction": f"Active Demo Scenario: {scenario['name']}. Proceed to inspect {scenario['well_id']}."
        }