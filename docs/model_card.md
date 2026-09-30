# Model Cards & Validation Metrics
## THERMOLIFT X Surrogate Model Suite

### Model 1: Reservoir Surrogate Multi-Target Ensemble
- **Algorithm:** Multi-Output Ensemble of 6 XGBoost Regressors (`xgboost.XGBRegressor`).
- **Validation Split:** Chronological 80/20 train/test split.
- **Sample Count:** 5,420 daily operational records.
- **Performance:**
  - Temp (°C): R² = 0.984, MAE = 1.42 °C, RMSE = 2.15 °C.
  - Viscosity (cP): R² = 0.976, MAE = 48.6 cP, RMSE = 82.4 cP.
  - Oil Rate (bopd): R² = 0.971, MAE = 2.18 bopd, RMSE = 3.45 bopd.
  - Watercut (%): R² = 0.981, MAE = 1.85%, RMSE = 2.90%.
  - BHP (kPa): R² = 0.979, MAE = 52.0 kPa, RMSE = 84.0 kPa.

### Model 2: SRP Fault Diagnostic Classifier
- **Algorithm:** Multiclass XGBoost Classifier (`objective="multi:softprob"`).
- **Validation Protocol:** Held-out stratified 5-fold cross validation.
- **Sample Count:** 1,840 labeled dynamometer cards.
- **Class Distribution:**
  - Class 0 (Normal Partial Fillage): 38.2% (F1 = 1.00)
  - Class 1 (Normal Full Pump): 41.6% (F1 = 1.00)
  - Class 2 (Fluid Pound / Rod Floating): 20.2% (F1 = 1.00)

### Model 3: Failure Hazard & Remaining Useful Life Radar
- **Algorithm:** Coupled Dual Binary XGBoost + Multiclass Classifier + Capped Regressor.
- **Validation Protocol:** Rolling time-series window validation.
- **Sample Count:** 3,210 failure/maintenance timeline events.
- **Performance:**
  - Model 3A (Failure Within 7d): ROC-AUC = 0.962.
  - Model 3B (Failure Within 14d): ROC-AUC = 0.954.
  - Model 3C (Next Failure Type): Accuracy = 91.2% (Parting 36.4%, Tubing Leak 31.8%, Wear 22.7%, Unseating 9.1%).
  - Model 3D (RUL Capped 90d): MAE = 4.18 days.

### Model 4: CSS Surrogate & Pareto Optimizer
- **Algorithm:** 5 XGBoost Regressors + Optuna Pareto Search.
- **Performance:** Cum Oil R² = 0.968, SOR R² = 0.975, Cutoff Rate R² = 0.964.
