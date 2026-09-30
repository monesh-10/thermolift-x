# Optimization & Supervisory Control Formulations

### 1. Joint Multi-Objective Objective Function
$$\text{Maximize } J = w_{\text{oil}} \cdot \hat{Q}_{\text{oil}} + w_{\text{energy}} \cdot \hat{E}_{\text{eff}} + w_{\text{rel}} \cdot (1 - \hat{P}_{7d}) + w_{\text{cost}} \cdot \hat{V}_{\text{net}} - \text{Penalty}(\text{Safety})$$

### 2. Safety Governor Hard Constraints
- $\text{SPM} \in [2.0, 10.5]$
- $\text{VFD Hz} \in [25.0, 65.0]$
- $\text{Floating Margin} \ge 15.0\%$
- $\text{Pump Fillage} \ge 75.0\%$
- $\text{PPRL} \le 22.0 \text{ klb}$
- $\text{Injection Pressure} \le 18,000 \text{ kPa}$
- $\text{Decision Confidence} \ge 0.75$

### 3. Knapsack Marginal Value of Steam (MVS)
$$\text{MVS} = \frac{\Delta \text{Oil (bbl)}}{\text{Steam CWE (m}^3\text{)}} \times (1 - \text{Risk}) \times \text{Confidence} \times \text{Net Profit Margin}$$
