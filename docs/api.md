# OpenAPI Reference (29 Active Endpoints)

| HTTP Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System status, active models, active field assets |
| `GET` | `/api/fleet/summary` | Aggregate fleet oil, water, SOR, active alerts |
| `GET` | `/api/well/{well_id}` | Live digital twin telemetry for specified well |
| `GET` | `/api/well/{well_id}/twin-state` | Enriched state with confidence, sensor coverage, and safety envelope |
| `GET` | `/api/well/{well_id}/timeline` | Historical operational time-series records |
| `POST` | `/api/well/{well_id}/optimize-vfd` | T-VFD supervisory speed recommendation |
| `POST` | `/api/well/{well_id}/apply-vfd` | Simulation dispatch of new SPM/Hz setpoints |
| `POST` | `/api/well/{well_id}/optimize-css` | Model 4 CSS Pareto steam cycle generator |
| `POST` | `/api/well/{well_id}/simulate-thermal` | 120-day thermal decay curve and floating onset day |
| `POST` | `/api/well/{well_id}/future-rehearsal` | Counterfactual forward simulation of 6 strategic branches |
| `POST` | `/api/well/{well_id}/joint-optimize` | Joint CSS + SRP multi-objective Pareto optimizer |
| `POST` | `/api/well/{well_id}/safety-check` | Safety Governor evaluation of operational envelope |
| `POST` | `/api/well/{well_id}/recommendation` | Structured incident recommendation (Observation, Cause, Prediction, Action) |
| `GET` | `/api/well/{well_id}/confidence` | Confidence Engine uncertainty, sensor coverage, data quality |
| `GET` | `/api/well/{well_id}/predicted-vs-actual` | Telemetry comparison table with absolute and percentage residuals |
| `POST` | `/api/well/{well_id}/feedback` | Log operator approval or rejection feedback |
| `POST` | `/api/well/{well_id}/recalibrate` | Online model recalibration and prior bias adjustment |
| `POST` | `/api/field/steam-allocation` | Fleet steam distribution by Marginal Value of Steam |
| `GET` | `/api/field/thermal-opportunity` | Field thermal distribution and top operational opportunities |
| `GET` | `/api/models/health` | Complete technical report for Models 1, 2, 3, and 4 |
| `GET` | `/api/twin/health` | Global Twin Health score, sub-indices, and model drift series |
| `GET` | `/api/jury/scenarios` | 5 deterministic scenarios and 13-step presentation sequence |
| `POST` | `/api/jury/run-scenario` | Activates specific jury scenario |
| `GET` | `/` | Serves main THERMOLIFT X web dashboard |
