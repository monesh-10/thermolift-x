"""Model Registry: Wraps and unifies all 4 AI/ML Surrogate Models for Baghewala Field.
1. Model 1: Reservoir Surrogate Agent (BHP, Oil Rate, Water Rate, Watercut, Temp, Viscosity)
2. Model 2: SRP Fault Diagnostic Agent (Classifies Dyno cards: Normal, Partial, Fluid Pound/Rod Floating)
3. Model 3: Failure & RUL Prediction Agent (7d hazard, 14d hazard, Next failure type, RUL days)
4. Model 4: CSS Optimization Surrogate Agent (Cum Oil, Cum Water, SOR, Production Days, Cutoff Rate)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_MAIN = Path(r"C:\Users\mones\.gemini\antigravity-ide\brain\974c7cd6-6c4e-4123-91e5-59adf4106ca4\scratch\digitwin120\digitwin120-main")
MODELS_DIR = SRC_MAIN / "models"


class ModelRegistry:
    _instance = None

    def __init__(self):
        self.reservoir_models: Dict[str, Any] = {}
        self.reservoir_preprocessor = None
        self.reservoir_metadata = {}

        self.srp_fault_model = None
        self.srp_fault_preprocessor = None
        self.srp_fault_metadata = {}

        self.failure_m7d = None
        self.failure_m14d = None
        self.failure_mnext = None
        self.failure_mrul = None
        self.failure_preprocessor = None

        self.css_models: Dict[str, Any] = {}
        self.css_preprocessor = None
        self.css_metadata = {}

        self.is_loaded = False
        self.load_all()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ModelRegistry()
        return cls._instance

    def load_all(self):
        if self.is_loaded:
            return

        print("[ModelRegistry] Loading Model 1: Reservoir Surrogate...")
        res_dir = MODELS_DIR / "reservoir"
        self.reservoir_preprocessor = joblib.load(res_dir / "preprocessor.joblib")
        with open(res_dir / "reservoir_metadata.json", "r", encoding="utf-8") as f:
            self.reservoir_metadata = json.load(f)
        for target in ["Reservoir_Wellbore_Temp_C", "Oil_Viscosity_cP", "Oil_Rate_bopd",
                       "Water_Rate_bwpd", "Watercut_pct", "Bottomhole_Pressure_kPa"]:
            self.reservoir_models[target] = joblib.load(res_dir / f"model_{target}.joblib")

        print("[ModelRegistry] Loading Model 2: SRP Fault Diagnostic...")
        srp_dir = MODELS_DIR / "srp_fault"
        self.srp_fault_preprocessor = joblib.load(srp_dir / "preprocessor.joblib")
        self.srp_fault_model = joblib.load(srp_dir / "model_srp_fault_xgboost.joblib")
        with open(srp_dir / "srp_fault_metadata.json", "r", encoding="utf-8") as f:
            self.srp_fault_metadata = json.load(f)

        print("[ModelRegistry] Loading Model 3: Failure & RUL...")
        fail_dir = MODELS_DIR / "failure"
        self.failure_preprocessor = joblib.load(fail_dir / "preprocessor.joblib")
        self.failure_m7d = joblib.load(fail_dir / "model_Failure_Within_7d.joblib")
        self.failure_m14d = joblib.load(fail_dir / "model_Failure_Within_14d.joblib")
        self.failure_mnext = joblib.load(fail_dir / "model_Next_Failure_Type.joblib")
        self.failure_mrul = joblib.load(fail_dir / "model_RUL_Capped_90d.joblib")

        print("[ModelRegistry] Loading Model 4: CSS Surrogate...")
        css_dir = MODELS_DIR / "css"
        self.css_preprocessor = joblib.load(css_dir / "preprocessor.joblib")
        with open(css_dir / "css_optimization_metadata.json", "r", encoding="utf-8") as f:
            self.css_metadata = json.load(f)
        for target in ["Cum_Oil_Produced_bbl", "Cum_Water_Produced_bbl", "Steam_Oil_Ratio_SOR",
                       "Production_Days_Actual", "Cutoff_Oil_Rate_bopd"]:
            self.css_models[target] = joblib.load(css_dir / f"model_{target}.joblib")

        self.is_loaded = True
        print("[ModelRegistry] All 4 AI models loaded successfully!")

    def predict_reservoir(self, features_dict: Dict[str, Any]) -> Dict[str, float]:
        """Predicts reservoir targets (Temp, Viscosity, Oil Rate, Water Rate, Watercut, BHP)."""
        feature_cols = self.reservoir_metadata.get("features", [])
        row = {c: features_dict.get(c, 0.0) for c in feature_cols}
        df_in = pd.DataFrame([row])
        X_trans = self.reservoir_preprocessor.transform(df_in)
        
        preds = {}
        for target, model in self.reservoir_models.items():
            val = float(model.predict(X_trans)[0])
            preds[target] = round(val, 2)
        return preds

    def predict_srp_fault(self, features_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnoses SRP operating condition: Normal (Partial), Normal (Full), Fluid Pound / Rod Floating."""
        feature_cols = self.srp_fault_metadata.get("features", [])
        row = {c: features_dict.get(c, 0.0) for c in feature_cols}
        df_in = pd.DataFrame([row])
        X_trans = self.srp_fault_preprocessor.transform(df_in)
        
        pred_class_id = int(self.srp_fault_model.predict(X_trans)[0])
        probas = self.srp_fault_model.predict_proba(X_trans)[0]
        
        labels = ["Normal (Partial)", "Normal (Full Pump)", "Fluid Pound / Rod Floating"]
        label = labels[pred_class_id] if pred_class_id < len(labels) else f"Class_{pred_class_id}"
        
        return {
            "predicted_class_id": pred_class_id,
            "predicted_label": label,
            "probabilities": {
                labels[i]: round(float(probas[i]), 4) for i in range(len(labels))
            }
        }

    def predict_failure_and_rul(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """Predicts 7-day and 14-day failure risk, next failure type, and RUL (days)."""
        X_trans = self.failure_preprocessor.transform(features_df)
        p7d = float(self.failure_m7d.predict_proba(X_trans)[0][1])
        p14d = float(self.failure_m14d.predict_proba(X_trans)[0][1])
        rul = float(self.failure_mrul.predict(X_trans)[0])
        next_type_idx = int(self.failure_mnext.predict(X_trans)[0])
        
        failure_type_map = {
            0: "Rod Parting",
            1: "Tubing Leak",
            2: "Worn Plunger/Barrel",
            3: "Pump Unseating"
        }
        next_type = failure_type_map.get(next_type_idx % 4, "Rod Parting")

        return {
            "prob_failure_7d": round(p7d, 4),
            "prob_failure_14d": round(p14d, 4),
            "rul_days": round(max(0.0, min(90.0, rul)), 1),
            "next_failure_type": next_type
        }

    def predict_css_outcomes(self, features_dict: Dict[str, Any]) -> Dict[str, float]:
        """Predicts CSS cycle outcomes (Cum Oil, Cum Water, SOR, Production Days, Cutoff Rate)."""
        expected_features = self.css_preprocessor.feature_names_in_
        row = {c: features_dict.get(c, 0.0) for c in expected_features}
        df_in = pd.DataFrame([row])
        X_trans = self.css_preprocessor.transform(df_in)

        outcomes = {}
        for target, model in self.css_models.items():
            val = float(model.predict(X_trans)[0])
            outcomes[target] = round(val, 2)
        return outcomes
