"""Confidence Engine: Quantifies Predictive Uncertainty, Sensor Health & Data Quality.
Every major prediction (production, temperature, viscosity, pump efficiency, failure risk,
optimization recommendation) must carry:
- prediction value
- confidence score [0.0 - 1.0]
- data quality score [0.0 - 1.0]
- model version
- sensor health status

If sensor data is missing/noisy or confidence < 0.75:
Sets: requires_operator_review = True -> "OPERATOR REVIEW REQUIRED".
"""

from typing import Dict, Any, List, Optional
import math


class ConfidenceEngine:
    MODEL_VERSIONS = {
        "model_1_reservoir": "v2.1.0-xgb-multitarget",
        "model_2_srp_fault": "v2.0.4-xgb-multiclass",
        "model_3_failure": "v2.2.1-xgb-hazard-rul",
        "model_4_css": "v2.1.0-xgb-optuna-pareto",
        "physics_engine": "v2.3.0-pinn-stokes-navier"
    }

    SENSOR_SPECS = [
        {"id": "THP", "name": "Wellhead Tubing Pressure", "unit": "kPa", "expected_min": 100.0, "expected_max": 2500.0},
        {"id": "CHP", "name": "Casing Annulus Pressure", "unit": "kPa", "expected_min": 50.0, "expected_max": 1800.0},
        {"id": "LOAD_CELL", "name": "Polished Rod Load Cell", "unit": "klb", "expected_min": 1.0, "expected_max": 24.0},
        {"id": "STROKE_POS", "name": "Surface Position Transducer", "unit": "in", "expected_min": 0.0, "expected_max": 144.0},
        {"id": "VFD_TACH", "name": "VFD Motor Frequency Tachometer", "unit": "Hz", "expected_min": 20.0, "expected_max": 65.0},
        {"id": "AMP_METER", "name": "Motor Current Transducer", "unit": "Amp", "expected_min": 5.0, "expected_max": 60.0},
        {"id": "TEMP_PROBE", "name": "Wellhead Flowline Temp Probe", "unit": "degC", "expected_min": 35.0, "expected_max": 200.0},
    ]

    @classmethod
    def evaluate_well_confidence(
        cls,
        well_state: Dict[str, Any],
        degraded_sensors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Evaluates sensor coverage, data quality, physical consistency and confidence."""
        degraded = degraded_sensors or []
        sensor_status: List[Dict[str, Any]] = []

        active_count = 0
        quality_penalties = 0.0

        for spec in cls.SENSOR_SPECS:
            sid = spec["id"]
            if sid in degraded:
                status = "MISSING" if sid == "LOAD_CELL" else "ANOMALOUS"
                freshness = "Stale (68 min ago)" if sid == "TEMP_PROBE" else "No Signal"
                quality = 0.30
            else:
                status = "NORMAL"
                freshness = "Realtime (< 2s)"
                quality = 1.00
                active_count += 1

            quality_penalties += (1.0 - quality)
            sensor_status.append({
                "sensor_id": sid,
                "name": spec["name"],
                "unit": spec["unit"],
                "status": status,
                "freshness": freshness,
                "health_score": round(quality * 100.0, 1),
                "is_active": status == "NORMAL"
            })

        total_sensors = len(cls.SENSOR_SPECS)
        sensor_coverage_pct = round((active_count / total_sensors) * 100.0, 1)
        data_quality_pct = round(max(30.0, 100.0 - (quality_penalties / total_sensors) * 100.0), 1)

        # Physics consistency check
        # Checks if temperature and viscosity follow physical inverse relationship
        temp_c = well_state.get("reservoir", {}).get("temperature_c", 50.0)
        visc_cp = well_state.get("reservoir", {}).get("oil_viscosity_cp", 3000.0)
        spm = well_state.get("surface_srp", {}).get("spm", 8.0)
        vfd_hz = well_state.get("surface_srp", {}).get("vfd_frequency_hz", 50.0)

        # Expected ratio: ~6.25 Hz per SPM
        ratio = vfd_hz / max(0.1, spm)
        vfd_kinematic_consistent = 5.0 <= ratio <= 7.5
        thermal_visc_consistent = (temp_c > 120.0 and visc_cp < 200.0) or (temp_c <= 60.0 and visc_cp > 1000.0) or (60.0 < temp_c <= 120.0)

        physics_consistency_pct = 98.0 if (vfd_kinematic_consistent and thermal_visc_consistent) else 82.0

        # Composite Prediction Confidence
        # Weighting: 40% Data Quality + 30% Sensor Coverage + 30% Physics Consistency
        comp_confidence = (
            (data_quality_pct / 100.0) * 0.40 +
            (sensor_coverage_pct / 100.0) * 0.30 +
            (physics_consistency_pct / 100.0) * 0.30
        )
        comp_confidence = round(min(0.99, max(0.35, comp_confidence)), 2)

        requires_review = comp_confidence < 0.75 or "MISSING" in [s["status"] for s in sensor_status]

        return {
            "overall_confidence": comp_confidence,
            "confidence_pct": round(comp_confidence * 100.0, 1),
            "data_quality_pct": data_quality_pct,
            "sensor_coverage_pct": sensor_coverage_pct,
            "physics_consistency_pct": physics_consistency_pct,
            "requires_operator_review": requires_review,
            "confidence_label": "HIGH CONFIDENCE" if comp_confidence >= 0.85 else ("MODERATE CONFIDENCE" if comp_confidence >= 0.75 else "OPERATOR REVIEW REQUIRED"),
            "model_versions": cls.MODEL_VERSIONS,
            "sensors": sensor_status,
            "audit_trail": {
                "vfd_kinematic_consistent": vfd_kinematic_consistent,
                "thermal_visc_consistent": thermal_visc_consistent,
                "active_sensors": f"{active_count}/{total_sensors}"
            }
        }