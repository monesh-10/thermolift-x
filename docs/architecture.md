# THERMOLIFT X — System Architecture
## Integrated Closed-Loop Thermal-to-Lift Decision Twin
**Smart India Hackathon (SIH 26120) | Oil India Limited (OIL)**

### 1. Conceptual Framework: OBSERVE -> UNDERSTAND -> PREDICT -> REHEARSE -> OPTIMIZE -> EXPLAIN -> VALIDATE -> LEARN
Unlike static SCADA dashboards, THERMOLIFT X couples first-principles thermodynamic and rod mechanics with machine-learning surrogates in a closed-loop decision architecture.

### 2. 7-Layer Cyber-Physical Architecture
1. **Layer 1: Physical Asset & Telemetry**
   - 15 Baghewala Field Heavy Oil Wells (BGW-001 through BGW-015) in Jodhpur Sandstone + BGW-017 Synthetic Demo Asset.
   - Sensor inputs: Wellhead Pressure, Casing Pressure, Load Cell (PPRL/MPRL), Position Transducer, VFD Tachometer, Motor Current, Flowline Temp.
2. **Layer 2: First-Principles Mechanics (PINN-Twin™)**
   - Stokes-Navier Annular Viscous Drag & Terminal Velocity Law.
   - Andrade-Walther Thermal Viscosity Decay Model.
   - Downhole Gibbs Wave Equation Dynamometer Card Synthesis.
3. **Layer 3: Multi-Target AI/ML Surrogates**
   - Model 1: Reservoir Surrogate Ensemble (6 XGBoost Regressors).
   - Model 2: SRP Fault Classifier (Multiclass XGBoost Classifier).
   - Model 3: Failure Hazard & RUL Radar (Dual XGBoost + RUL Regressor).
   - Model 4: CSS Cycle Optimizer (5 XGBoost Regressors + Optuna Pareto).
4. **Layer 4: Counterfactual Future Rehearsal**
   - 6 Parallel forward branches simulated over 7d, 14d, 30d (Current, More Steam, Longer Soak, Change SRP, Combined, Optimized).
5. **Layer 5: Joint CSS + SRP Decision Optimizer**
   - Jointly tunes steam parameters and surface speeds.
   - Multi-objective profiles: Production-First, Energy-First, Reliability-First, Cost-First, Balanced.
6. **Layer 6: Safety Governor & Operating Envelope**
   - Hard engineering constraints: positive rod fall margin, motor SPM/Hz, fracture pressure, rod string stress.
7. **Layer 7: Feedback, Drift Detection & Recalibration**
   - Compares predicted vs observed telemetry; calculates residuals, monitors model drift, updates Bayesian priors.
