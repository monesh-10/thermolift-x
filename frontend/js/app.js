/**
 * THERMOLIFT X — Master Application Controller
 * Baghewala Heavy Oil Well-to-Surface Predictive Decision Twin | SIH 26120
 */

const API_BASE = window.location.origin;

let rigVisualizer = null;
let dynoPlotter = null;

let currentWellId = "BGW-002";
let currentWellState = null;
let currentFleetSummary = null;
let currentJuryStepIndex = 0;
let jurySteps = [];

document.addEventListener("DOMContentLoaded", () => {
  initDrawer();
  initRenderers();
  initNavigation();
  initEventListeners();
  loadFleetOverview();
  loadWellData(currentWellId);
  loadModelHealth();
  initJurySteps();
});

function initRenderers() {
  rigVisualizer = new RigRenderer("rigCanvas");
  dynoPlotter = new DynoRenderer("dynoCanvas");
}

function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const targetView = item.getAttribute("data-target");
      switchView(targetView);
    });
  });
}

function switchView(viewId) {
  document.querySelectorAll(".nav-item").forEach(item => {
    if (item.getAttribute("data-target") === viewId) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });

  document.querySelectorAll(".view-pane").forEach(pane => {
    pane.classList.remove("active");
  });

  const activePane = document.getElementById(viewId);
  if (activePane) {
    activePane.classList.add("active");
  }

  // Trigger canvas resize
  setTimeout(() => {
    if (rigVisualizer) rigVisualizer.resizeCanvas();
    if (dynoPlotter) dynoPlotter.resizeCanvas();
  }, 50);
}

function initEventListeners() {
  const wellSelect = document.getElementById("wellSelect");
  if (wellSelect) {
    wellSelect.addEventListener("change", (e) => {
      currentWellId = e.target.value;
      loadWellData(currentWellId);
    });
  }

  const btnRehearse = document.getElementById("btnRunFutureRehearsal");
  if (btnRehearse) {
    btnRehearse.addEventListener("click", runFutureRehearsal);
  }

  const btnJointOpt = document.getElementById("btnExecuteJointOpt");
  if (btnJointOpt) {
    btnJointOpt.addEventListener("click", runJointOptimization);
  }

  const btnAllocate = document.getElementById("btnAllocateSteam");
  if (btnAllocate) {
    btnAllocate.addEventListener("click", allocateFieldSteam);
  }

  const rngSteam = document.getElementById("rngAvailableSteam");
  if (rngSteam) {
    rngSteam.addEventListener("input", (e) => {
      document.getElementById("lblAvailableSteamVal").innerText = Number(e.target.value).toLocaleString() + " m³";
    });
  }

  const btnRecal = document.getElementById("btnRecalibrateTwin");
  if (btnRecal) {
    btnRecal.addEventListener("click", recalibrateTwin);
  }

  const btnApprove = document.getElementById("btnApproveSimulation");
  if (btnApprove) {
    btnApprove.addEventListener("click", approveSimulationDispatch);
  }

  const btnSimulate = document.getElementById("btnSimulateIntervention");
  if (btnSimulate) {
    btnSimulate.addEventListener("click", approveSimulationDispatch);
  }

  const btnOpenJury = document.getElementById("btnOpenJuryMode");
  const btnCloseJury = document.getElementById("btnCloseJuryModal");
  if (btnOpenJury) {
    btnOpenJury.addEventListener("click", openJuryModal);
  }
  if (btnCloseJury) {
    btnCloseJury.addEventListener("click", closeJuryModal);
  }

  const btnJuryNext = document.getElementById("btnJuryNext");
  const btnJuryPrev = document.getElementById("btnJuryPrev");
  if (btnJuryNext) {
    btnJuryNext.addEventListener("click", nextJuryStep);
  }
  if (btnJuryPrev) {
    btnJuryPrev.addEventListener("click", prevJuryStep);
  }
}

async function loadFleetOverview() {
  try {
    const res = await fetch(`${API_BASE}/api/fleet/summary`);
    const data = await res.json();
    currentFleetSummary = data;

    document.getElementById("kpiFieldOil").innerText = data.total_oil_rate_bopd.toFixed(1) + " bopd";
    document.getElementById("kpiFieldWater").innerText = data.total_water_rate_bwpd.toFixed(1) + " bwpd";
    document.getElementById("kpiFieldSor").innerText = data.average_sor.toFixed(2) + " m³/m³";
    document.getElementById("kpiFieldKwhBbl").innerText = (data.total_daily_kwh / Math.max(1, data.total_oil_rate_bopd)).toFixed(1) + " kWh/bbl";
    document.getElementById("kpiActiveAlerts").innerText = (data.status_distribution.critical + data.status_distribution.warning);

    // Fleet Grid
    const gridEl = document.getElementById("fleetGridContainer");
    if (gridEl) {
      gridEl.innerHTML = "";
      data.wells.forEach(w => {
        const chip = document.createElement("div");
        chip.className = "fleet-well-chip";
        const dotClass = w.status === "CRITICAL" ? "critical" : (w.status === "WARNING" ? "warning" : "healthy");
        chip.innerHTML = `
          <div class="well-chip-header">
            <span class="well-chip-id">${w.well_id} ${w.is_demo_asset ? '<span style="font-size:0.6rem; color:var(--purple-opt)">[DEMO]</span>' : ''}</span>
            <div class="status-dot ${dotClass}"></div>
          </div>
          <div class="well-chip-data">
            <div>Oil: <strong>${w.oil_rate_bopd.toFixed(1)}</strong> bopd</div>
            <div>Temp: <strong>${w.temperature_c.toFixed(1)}°C</strong></div>
            <div>SPM: <strong>${w.spm.toFixed(1)}</strong> (${w.vfd_hz.toFixed(1)} Hz)</div>
            <div>Margin: <span style="color:${w.floating_margin_pct <= 0 ? 'var(--rose-critical)' : (w.floating_margin_pct < 15 ? 'var(--amber-warning)' : 'var(--emerald-healthy)')}">${w.floating_margin_pct.toFixed(0)}%</span></div>
          </div>
        `;
        chip.addEventListener("click", () => {
          const wellSel = document.getElementById("wellSelect");
          if (wellSel) wellSel.value = w.well_id;
          currentWellId = w.well_id;
          loadWellData(w.well_id);
          switchView("view-well-intelligence");
        });
        gridEl.appendChild(chip);
      });
    }

    // Top Risks & Opportunities
    const oppRes = await fetch(`${API_BASE}/api/field/thermal-opportunity`);
    const oppData = await oppRes.json();
    const risksEl = document.getElementById("topRisksContainer");
    if (risksEl) {
      risksEl.innerHTML = oppData.top_risks.map(r => `
        <div style="background: rgba(239,68,68,0.08); border-left: 3px solid var(--rose-critical); padding: 8px 12px; margin-bottom: 8px; border-radius: var(--radius-sm); font-size: 0.8rem; font-family: var(--font-mono);">
          <strong>${r.well_id}</strong>: ${r.issue} &bull; Margin: ${r.margin_pct.toFixed(1)}% &bull; P7d: ${r.failure_risk_7d.toFixed(2)}
        </div>
      `).join("");
    }

    const oppsEl = document.getElementById("topOpportunitiesContainer");
    if (oppsEl) {
      oppsEl.innerHTML = oppData.top_opportunities.map(o => `
        <div style="background: rgba(16,185,129,0.08); border-left: 3px solid var(--emerald-healthy); padding: 8px 12px; margin-bottom: 8px; border-radius: var(--radius-sm); font-size: 0.8rem; font-family: var(--font-mono);">
          <strong>${o.well_id}</strong> (${o.temp_c.toFixed(1)}°C, ${o.oil_rate_bopd.toFixed(1)} bopd): ${o.recommendation}
        </div>
      `).join("");
    }
  } catch (err) {
    console.error("Failed to load fleet overview:", err);
  }
}

async function loadWellData(wellId) {
  try {
    const res = await fetch(`${API_BASE}/api/well/${wellId}/twin-state`);
    const data = await res.json();
    currentWellState = data.state;

    const state = data.state;
    const resv = state.reservoir;
    const srp = state.surface_srp;
    const mech = state.mechanics;
    const fail = state.failure_prediction;
    const diag = state.diagnostics;

    document.getElementById("wellIntellTitle").innerText = `WELL INTELLIGENCE — ${wellId} ${state.is_demo_asset ? '[DEMO ASSET]' : ''}`;
    document.getElementById("wiTemp").innerText = resv.temperature_c.toFixed(1) + " °C";
    document.getElementById("wiVisc").innerText = Math.round(resv.oil_viscosity_cp).toLocaleString() + " cP";
    document.getElementById("wiOil").innerText = resv.oil_rate_bopd.toFixed(1) + " bopd";
    document.getElementById("wiWatercut").innerText = resv.watercut_pct.toFixed(0) + "%";
    document.getElementById("wiSpm").innerText = srp.spm.toFixed(1) + " SPM";
    document.getElementById("wiVfd").innerText = srp.vfd_frequency_hz.toFixed(1) + " Hz";

    const marginEl = document.getElementById("wiMargin");
    marginEl.innerText = mech.floating_margin_pct.toFixed(1) + "%";
    marginEl.style.color = mech.floating_margin_pct <= 0 ? "var(--rose-critical)" : (mech.floating_margin_pct < 15 ? "var(--amber-warning)" : "var(--emerald-healthy)");
    document.getElementById("wiMarginStatus").innerText = mech.is_rod_floating ? "CRITICAL: SLACK BRIDLE" : "Safe positive sink";

    document.getElementById("wiFailRisk").innerText = fail.prob_failure_7d.toFixed(2);
    document.getElementById("wiRul").innerText = fail.rul_days.toFixed(1) + " days";

    // Explanations
    document.getElementById("wiExplanationText").innerText =
      `Well ${wellId} produces from Jodhpur Sandstone (depth ${state.metadata.Pump_Depth_m || 1000}m TVD) at ${resv.temperature_c.toFixed(1)}°C. ` +
      `Thermal decay after steam cycle #${state.cycle_no} has caused crude viscosity to rise to ${Math.round(resv.oil_viscosity_cp)} cP. ` +
      (mech.is_rod_floating
        ? `This generates annular shear drag exceeding the buoyant rod weight, triggering rod floating and slack-bridle impact shock loading (4.8 klb). Pumping speed (${srp.spm.toFixed(1)} SPM) must be lowered to ${mech.max_safe_spm.toFixed(1)} SPM.`
        : `Annular drag is within manageable limits. Current floating margin is +${mech.floating_margin_pct.toFixed(1)}%. Operation is currently stable.`);

    document.getElementById("wiActionText").innerText =
      mech.is_rod_floating
        ? `T-VFD Recommended: Throttle VFD from ${srp.vfd_frequency_hz.toFixed(1)} Hz to ${(mech.max_safe_spm * 6.25).toFixed(1)} Hz (${mech.max_safe_spm.toFixed(1)} SPM) to restore positive rod sinking.`
        : `Hold steady pumping setpoints (${srp.spm.toFixed(1)} SPM). Monitor thermal cooling trajectory for upcoming steam injection window.`;

    // Digital Twin Canvas
    if (rigVisualizer) rigVisualizer.updateState(state);

    // Digital Twin Telemetry
    document.getElementById("dtTermVel").innerText = mech.v_terminal_mps.toFixed(3) + " m/s";
    document.getElementById("dtPeakPrVel").innerText = mech.v_pr_max_mps.toFixed(3) + " m/s";
    document.getElementById("dtFloatingMargin").innerText = mech.floating_margin_pct.toFixed(1) + "%";
    document.getElementById("dtFloatingMargin").style.color = mech.floating_margin_pct <= 0 ? "var(--rose-critical)" : (mech.floating_margin_pct < 15 ? "var(--amber-warning)" : "var(--emerald-healthy)");
    document.getElementById("dtFloatingCondition").innerText = mech.is_rod_floating ? "FLOATING DETECTED — CARRIER SEPARATION" : "SAFE POSITIVE FALL";
    document.getElementById("dtImpactForce").innerText = mech.impact_force_klb.toFixed(2) + " klb";

    // Dyno Card Canvas
    if (dynoPlotter) dynoPlotter.updateData(state.dyno_cards);
    document.getElementById("dynoPprlVal").innerText = mech.pprl_klb.toFixed(2) + " klb";
    document.getElementById("dynoMprlVal").innerText = mech.mprl_klb.toFixed(2) + " klb";
    document.getElementById("dynoDeltaVal").innerText = (mech.pprl_klb - mech.mprl_klb).toFixed(2) + " klb";
    document.getElementById("dynoAreaVal").innerText = state.dyno_cards.card_area_klb_in.toFixed(1) + " klb·in";

    // Model 2 Diagnosis
    document.getElementById("dynoDiagnosisLabel").innerText = diag.predicted_label;
    document.getElementById("dynoDiagConfidence").innerText = (Math.max(...Object.values(diag.probabilities)) * 100).toFixed(1) + "%";
    document.getElementById("probFull").innerText = ((diag.probabilities["Normal (Full Pump)"] || 0) * 100).toFixed(1) + "%";
    document.getElementById("barFull").style.width = ((diag.probabilities["Normal (Full Pump)"] || 0) * 100) + "%";
    document.getElementById("probPartial").innerText = ((diag.probabilities["Normal (Partial)"] || 0) * 100).toFixed(1) + "%";
    document.getElementById("barPartial").style.width = ((diag.probabilities["Normal (Partial)"] || 0) * 100) + "%";
    document.getElementById("probFloating").innerText = ((diag.probabilities["Fluid Pound / Rod Floating"] || 0) * 100).toFixed(1) + "%";
    document.getElementById("barFloating").style.width = ((diag.probabilities["Fluid Pound / Rod Floating"] || 0) * 100) + "%";

    // Reliability Radar
    document.getElementById("rrP7d").innerText = fail.prob_failure_7d.toFixed(2);
    document.getElementById("rrP14d").innerText = fail.prob_failure_14d.toFixed(2);
    document.getElementById("rrRul").innerText = fail.rul_days.toFixed(1) + " days";
    document.getElementById("rrNextFail").innerText = fail.next_failure_type;
    document.getElementById("rrDriverText").innerText =
      `Current primary hazard driver is ${fail.next_failure_type}. ` +
      (mech.is_rod_floating ? `Severe cyclic impact loading (shock cycles: 1,420) increases rod parting probability to 86%.` : `Operating within normal mechanical fatigue envelope.`);

    // Decision Center
    document.getElementById("decWellHeader").innerText = `OPERATOR DISPATCH AUDIT — ${wellId}`;
    const safety = data.safety || state.safety || {};
    const badgeEl = document.getElementById("decSafetyBadge");
    if (badgeEl) {
      badgeEl.innerText = safety.status || "PASSED";
      badgeEl.className = `badge-item ${safety.badge === 'RED' ? 'badge-prototype' : (safety.badge === 'AMBER' ? 'badge-prototype' : 'badge-wells')}`;
    }

    document.getElementById("decRationaleText").innerHTML = `
      <strong>OBSERVATION:</strong> Well ${wellId} exhibits wellbore temperature of ${resv.temperature_c.toFixed(1)}°C with crude viscosity estimated at ${Math.round(resv.oil_viscosity_cp)} cP.<br>
      <strong>CAUSE:</strong> Post-steam thermal decay increases viscous drag on the rod string.<br>
      <strong>PREDICTION:</strong> Without intervention, floating margin remains at ${mech.floating_margin_pct.toFixed(1)}%, creating ongoing cyclic shock stress.<br>
      <strong>ACTION:</strong> Dispatch T-VFD setpoint to ${mech.max_safe_spm.toFixed(1)} SPM (${(mech.max_safe_spm * 6.25).toFixed(1)} Hz).<br>
      <strong>CONFIDENCE:</strong> ${data.confidence.confidence_pct}% (${data.confidence.confidence_label})
    `;

    const safetyList = document.getElementById("decSafetyChecksList");
    if (safetyList && safety.checks) {
      safetyList.innerHTML = safety.checks.map(c => `
        <div style="display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px dashed rgba(255,255,255,0.06);">
          <span>${c.parameter}:</span>
          <span style="color:${c.passed ? 'var(--emerald-healthy)' : 'var(--rose-critical)'}"><strong>${c.value}</strong> [${c.passed ? 'PASS' : 'FAIL'}]</span>
        </div>
      `).join("");
    }

    // Predicted vs Actual Table
    const pa = data.predicted_vs_actual;
    if (pa && pa.parameters) {
      document.getElementById("paMeanError").innerText = pa.mean_prediction_error_pct.toFixed(1) + "%";
      const tableBody = document.querySelector("#predActualTable tbody");
      if (tableBody) {
        tableBody.innerHTML = pa.parameters.map(p => `
          <tr>
            <td><strong>${p.parameter}</strong></td>
            <td>${p.unit}</td>
            <td style="color:var(--cyan-primary)">${p.predicted}</td>
            <td>${p.actual}</td>
            <td>${p.absolute_error}</td>
            <td>${p.error_pct.toFixed(1)}%</td>
            <td><span style="color:var(--emerald-healthy)">${p.status}</span></td>
          </tr>
        `).join("");
      }
    }
  } catch (err) {
    console.error("Failed to load well data:", err);
  }
}

async function runFutureRehearsal() {
  const container = document.getElementById("rehearsalCardsContainer");
  if (!container) return;
  container.innerHTML = "<div style='color:var(--cyan-primary); padding:20px; font-family:var(--font-mono)'>Simulating 6 parallel counterfactual branches over 30 days...</div>";

  try {
    const res = await fetch(`${API_BASE}/api/well/${currentWellId}/future-rehearsal`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    const data = await res.json();

    container.innerHTML = "";
    data.branches.forEach(b => {
      const isOpt = b.branch_id === "BRANCH_F";
      const card = document.createElement("div");
      card.className = `rehearsal-card ${isOpt ? 'optimized' : ''}`;
      card.innerHTML = `
        <div class="rehearsal-badge" style="background:${b.color}22; color:${b.color}; border:1px solid ${b.color}55;">
          ${b.branch_id}: ${b.type}
        </div>
        <div class="rehearsal-title">${b.name}</div>
        <div class="rehearsal-stat-row">
          <span class="rehearsal-stat-label">30-Day Cum Oil:</span>
          <span class="rehearsal-stat-val" style="color:var(--cyan-primary)">${b.summary_30d.cum_oil_bbl.toLocaleString()} bbl</span>
        </div>
        <div class="rehearsal-stat-row">
          <span class="rehearsal-stat-label">Steam-Oil Ratio (SOR):</span>
          <span class="rehearsal-stat-val">${b.summary_30d.sor.toFixed(2)}</span>
        </div>
        <div class="rehearsal-stat-row">
          <span class="rehearsal-stat-label">Specific Energy:</span>
          <span class="rehearsal-stat-val">${b.summary_30d.avg_specific_energy_kwh_bbl.toFixed(2)} kWh/bbl</span>
        </div>
        <div class="rehearsal-stat-row">
          <span class="rehearsal-stat-label">Net 30d Value:</span>
          <span class="rehearsal-stat-val" style="color:${b.summary_30d.net_value_lakhs_inr >= 0 ? 'var(--emerald-healthy)' : 'var(--rose-critical)'}">₹${b.summary_30d.net_value_lakhs_inr.toFixed(1)} Lakhs</span>
        </div>
        <div class="rehearsal-stat-row">
          <span class="rehearsal-stat-label">Rod Fall Margin:</span>
          <span class="rehearsal-stat-val" style="color:${b.summary_30d.terminal_floating_margin_pct <= 0 ? 'var(--rose-critical)' : 'var(--emerald-healthy)'}">${b.summary_30d.terminal_floating_margin_pct.toFixed(1)}%</span>
        </div>
        <div class="rehearsal-stat-row">
          <span class="rehearsal-stat-label">Safety Status:</span>
          <span class="rehearsal-stat-val" style="color:${b.summary_30d.is_permissible ? 'var(--emerald-healthy)' : 'var(--rose-critical)'}">${b.summary_30d.safety_status}</span>
        </div>
      `;
      container.appendChild(card);
    });

    document.getElementById("whyOptimizedWinsText").innerHTML = `
      <strong>ANALYTICAL SYNTHESIS:</strong> ${data.why_optimized_wins}<br>
      <div style="margin-top:10px; font-size:0.75rem; color:var(--text-dim); font-family:var(--font-mono)">
        ${data.disclaimer}
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div style="color:var(--rose-critical)">Simulation failed: ${err.message}</div>`;
  }
}

async function runJointOptimization() {
  const tableBody = document.querySelector("#jointOptTable tbody");
  if (!tableBody) return;
  tableBody.innerHTML = "<tr><td colspan='8' style='text-align:center; color:var(--cyan-primary); padding:20px'>Searching multi-objective Pareto strategy space...</td></tr>";

  const profile = document.getElementById("optProfileSelect")?.value || "balanced";
  const wOil = parseFloat(document.getElementById("rngWeightOil")?.value || 0.6);
  const wEnergy = parseFloat(document.getElementById("rngWeightEnergy")?.value || 0.5);
  const wRel = parseFloat(document.getElementById("rngWeightRel")?.value || 0.6);

  try {
    const res = await fetch(`${API_BASE}/api/well/${currentWellId}/joint-optimize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        profile: profile,
        custom_weights: { w_oil: wOil, w_energy: wEnergy, w_rel: wRel, w_cost: 0.5, w_sor: 0.4 }
      })
    });
    const data = await res.json();

    tableBody.innerHTML = "";
    data.all_strategies.forEach(s => {
      const isTop = s.strategy_id === data.recommended_strategy.strategy_id;
      const tr = document.createElement("tr");
      if (isTop) tr.style.background = "rgba(16,185,129,0.08)";
      tr.innerHTML = `
        <td><strong>${s.name}</strong> ${isTop ? '<span style="color:var(--emerald-healthy); font-size:0.7rem;">[RECOMMENDED]</span>' : ''}</td>
        <td>${s.css_parameters.steam_volume_cwe_m3 > 0 ? s.css_parameters.steam_volume_cwe_m3 + ' m³' : 'None'}</td>
        <td>${s.srp_parameters.spm.toFixed(1)} SPM (${s.srp_parameters.vfd_hz.toFixed(1)} Hz)</td>
        <td style="color:var(--cyan-primary)">${s.predicted_outcomes.oil_rate_bopd.toFixed(1)} bopd</td>
        <td>${s.predicted_outcomes.sor.toFixed(2)}</td>
        <td>${s.predicted_outcomes.specific_energy_kwh_per_bbl.toFixed(1)}</td>
        <td><span style="color:${s.safety.is_permissible ? 'var(--emerald-healthy)' : 'var(--rose-critical)'}">${s.safety.status}</span></td>
        <td>
          <button class="btn-primary" style="font-size:0.72rem; padding:4px 8px;" onclick="applyStrategyFromTable('${s.srp_parameters.spm}', '${s.srp_parameters.vfd_hz}')">SIMULATE</button>
        </td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan='8' style='color:var(--rose-critical)'>Optimization failed: ${err.message}</td></tr>`;
  }
}

function applyStrategyFromTable(spm, vfdHz) {
  fetch(`${API_BASE}/api/well/${currentWellId}/apply-vfd`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ spm: parseFloat(spm), vfd_hz: parseFloat(vfdHz) })
  }).then(r => r.json()).then(data => {
    alert(data.message);
    loadWellData(currentWellId);
    loadFleetOverview();
  });
}

async function allocateFieldSteam() {
  const tableBody = document.querySelector("#steamAllocTable tbody");
  if (!tableBody) return;
  tableBody.innerHTML = "<tr><td colspan='9' style='text-align:center; color:var(--cyan-primary); padding:20px'>Calculating knapsack Marginal Value of Steam...</td></tr>";

  const avail = parseFloat(document.getElementById("rngAvailableSteam")?.value || 8500);

  try {
    const res = await fetch(`${API_BASE}/api/field/steam-allocation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ available_steam_m3: avail })
    });
    const data = await res.json();

    document.getElementById("lblAllocationSummary").innerText =
      `Allocated ${data.total_allocated_steam_m3.toLocaleString()} m³ across ${data.allocated_wells_count} wells. Fleet SOR: ${data.projected_fleet_sor.toFixed(2)}`;

    tableBody.innerHTML = "";
    data.allocation_table.forEach(c => {
      const tr = document.createElement("tr");
      if (c.allocated) tr.style.background = "rgba(16,185,129,0.08)";
      tr.innerHTML = `
        <td><strong>#${c.allocation_rank}</strong></td>
        <td><strong>${c.well_id}</strong></td>
        <td><span style="color:${c.thermal_color}; font-weight:700;">${c.thermal_state} (${c.temperature_c}°C)</span></td>
        <td>${c.current_oil_bopd.toFixed(1)}</td>
        <td style="color:var(--cyan-primary)">+${c.incremental_oil_bbl.toLocaleString()} bbl</td>
        <td>${c.steam_required_m3.toLocaleString()} m³</td>
        <td>${c.projected_sor.toFixed(2)}</td>
        <td style="color:${c.marginal_value_inr_per_m3 > 0 ? 'var(--emerald-healthy)' : 'var(--text-dim)'}">₹${c.marginal_value_inr_per_m3.toLocaleString()}</td>
        <td><span style="color:${c.allocated ? 'var(--emerald-healthy)' : (c.thermal_state === 'HOT' ? 'var(--amber-warning)' : 'var(--text-dim)')}"><strong>${c.recommendation}</strong></span></td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan='9' style='color:var(--rose-critical)'>Steam allocation failed: ${err.message}</td></tr>`;
  }
}

async function recalibrateTwin() {
  const btn = document.getElementById("btnRecalibrateTwin");
  if (btn) btn.innerText = "Recalibrating...";
  try {
    const res = await fetch(`${API_BASE}/api/well/${currentWellId}/recalibrate`, { method: "POST" });
    const data = await res.json();
    alert(data.message);
    document.getElementById("paLastRecal").innerText = data.calibration_state.last_recalibrated;
    const healthScore = (data.new_health_score && typeof data.new_health_score === 'object')
      ? data.new_health_score.overall_twin_health_pct
      : (data.new_health_score || "92.8");
    document.getElementById("headerTwinHealthBadge").innerHTML = `<span class="badge-status-dot live"></span> TWIN HEALTH: ${healthScore}%`;
    const paEl = document.getElementById("paTwinHealth");
    if (paEl) paEl.innerText = `${healthScore}%`;
    loadWellData(currentWellId);
  } catch (err) {
    alert("Recalibration failed: " + err.message);
  } finally {
    if (btn) btn.innerHTML = `<svg class="btn-icon" viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg> RECALIBRATE TWIN`;
  }
}

async function approveSimulationDispatch() {
  try {
    const targetSpm = currentWellState.mechanics.is_rod_floating ? currentWellState.mechanics.max_safe_spm : currentWellState.surface_srp.spm;
    const targetVfd = targetSpm * 6.25;

    const res = await fetch(`${API_BASE}/api/well/${currentWellId}/apply-vfd`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ spm: targetSpm, vfd_hz: targetVfd })
    });
    const data = await res.json();
    alert(data.message);
    loadWellData(currentWellId);
    loadFleetOverview();
    switchView("view-digital-twin");
  } catch (err) {
    alert("Dispatch simulation failed: " + err.message);
  }
}

async function loadModelHealth() {
  const container = document.getElementById("modelHealthCardsContainer");
  if (!container) return;
  try {
    const res = await fetch(`${API_BASE}/api/models/health`);
    const data = await res.json();
    container.innerHTML = "";

    data.models.forEach(m => {
      const card = document.createElement("div");
      card.className = "panel-card";
      let metricsHtml = "";
      if (m.metrics) {
        metricsHtml = `<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin-top:10px; font-family:var(--font-mono); font-size:0.75rem;">` +
          m.metrics.map(met => `
            <div style="background:rgba(0,0,0,0.3); padding:8px; border-radius:4px; border:1px solid var(--border-subtle);">
              <div style="color:var(--text-dim)">${met.target || met.class_label || met.sub_model}</div>
              <div>${met.r2 ? 'R²: <strong>' + met.r2 + '</strong>' : (met.precision ? 'F1: <strong>' + met.f1_score + '</strong>' : 'Value: <strong>' + met.value + '</strong>')}</div>
              ${met.mae ? '<div style="color:var(--text-muted)">MAE: ' + met.mae + ' ' + (met.unit || '') + '</div>' : ''}
            </div>
          `).join("") + `</div>`;
      }

      card.innerHTML = `
        <div class="panel-title">
          <span>${m.title}</span>
          <span class="badge-item badge-twin-health">${m.version}</span>
        </div>
        <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:8px;">
          Architecture: <strong>${m.architecture}</strong> &bull; Protocol: <strong>${m.validation_protocol}</strong> (Samples: ${m.sample_count})
        </div>
        ${metricsHtml}
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error("Failed to load model health:", err);
  }
}

// =========================================================================
// SCADA FIELD INCIDENT REPLAY & AUDIT TRAIL (13 PHASES)
// =========================================================================

async function initJurySteps() {
  try {
    const res = await fetch(`${API_BASE}/api/jury/scenarios`);
    const data = await res.json();
    jurySteps = data.jury_steps;
  } catch (err) {
    console.error("Failed to load jury steps:", err);
  }
}

function openJuryModal() {
  currentJuryStepIndex = 0;
  const modal = document.getElementById("juryModalBackdrop");
  if (modal) modal.classList.add("active");
  renderJuryStep();
}

function closeJuryModal() {
  const modal = document.getElementById("juryModalBackdrop");
  if (modal) modal.classList.remove("active");
}

function renderJuryStep() {
  if (!jurySteps || jurySteps.length === 0) return;
  const step = jurySteps[currentJuryStepIndex];

  document.getElementById("juryStepBadge").innerText = `PHASE ${step.step} OF ${jurySteps.length} • SCADA AUDIT TRAIL`;
  document.getElementById("juryStepTitle").innerText = step.title;
  document.getElementById("juryQuestionBox").innerText = `DIAGNOSTIC FOCUS: ${step.key_question}`;
  const narrativeBox = document.getElementById("juryNarrativeBox");
  if (narrativeBox) {
    narrativeBox.innerHTML = `
      <div class="log-label">
        <svg class="btn-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        SCADA FIELD TELEMETRY & SUPERVISORY RATIONALE
      </div>
      <div class="log-body">${step.narrative_statement}</div>
    `;
  }

  const pointsContainer = document.getElementById("juryKeyPointsContainer");
  if (pointsContainer && step.key_data_points) {
    pointsContainer.innerHTML = step.key_data_points.map(p => `
      <div class="jury-point-chip">${p}</div>
    `).join("");
  }

  // Progress dots
  const dotsContainer = document.getElementById("juryProgressDots");
  if (dotsContainer) {
    dotsContainer.innerHTML = jurySteps.map((s, idx) => `
      <div class="p-dot ${idx === currentJuryStepIndex ? 'active' : ''}"></div>
    `).join("");
  }

  // Auto-switch view corresponding to step
  if (step.target_view) {
    switchView(`view-${step.target_view.replace('_', '-')}`);
  }

  // Trigger special step actions
  if (step.action_trigger === "select_well_bgw002") {
    currentWellId = "BGW-002";
    const sel = document.getElementById("wellSelect");
    if (sel) sel.value = "BGW-002";
    loadWellData("BGW-002");
  } else if (step.action_trigger === "run_future_rehearsal") {
    runFutureRehearsal();
  } else if (step.action_trigger === "run_joint_optimization") {
    runJointOptimization();
  } else if (step.action_trigger === "approve_simulation_dispatch") {
    approveSimulationDispatch();
  } else if (step.action_trigger === "recalibrate_twin_step") {
    recalibrateTwin();
  } else if (step.action_trigger === "open_field_steam") {
    allocateFieldSteam();
  }
}

function nextJuryStep() {
  if (currentJuryStepIndex < jurySteps.length - 1) {
    currentJuryStepIndex++;
    renderJuryStep();
  } else {
    closeJuryModal();
    // Incident replay sequence complete
  }
}

function prevJuryStep() {
  if (currentJuryStepIndex > 0) {
    currentJuryStepIndex--;
    renderJuryStep();
  }
}


// =========================================================================
// SLIDE-OUT DATA DRAWER LOGIC (ALL LISTS & TABLES)
// =========================================================================

function initDrawer() {
  const drawer = document.getElementById("dataDrawer");
  const backdrop = document.getElementById("dataDrawerBackdrop");
  const btnClose = document.getElementById("btnCloseDrawer");
  const btnToggle = document.getElementById("btnToggleDrawer");
  const btnSidebar = document.getElementById("btnOpenDrawerSidebar");
  const btnDeck = document.getElementById("btnOpenDrawerFromDeck");

  function openDrawer(targetTabId) {
    if (drawer) drawer.classList.add("open");
    if (backdrop) backdrop.classList.add("active");
    if (targetTabId) {
      switchDrawerTab(targetTabId);
    }
  }

  function closeDrawer() {
    if (drawer) drawer.classList.remove("open");
    if (backdrop) backdrop.classList.remove("active");
    setTimeout(() => {
      if (rigVisualizer) rigVisualizer.resizeCanvas();
      if (dynoPlotter) dynoPlotter.resizeCanvas();
    }, 100);
  }

  if (btnToggle) btnToggle.addEventListener("click", () => {
    if (drawer && drawer.classList.contains("open")) {
      closeDrawer();
    } else {
      openDrawer();
    }
  });

  if (btnSidebar) btnSidebar.addEventListener("click", () => openDrawer("tab-fleet"));
  if (btnDeck) btnDeck.addEventListener("click", () => openDrawer("tab-fleet"));
  if (btnClose) btnClose.addEventListener("click", closeDrawer);
  if (backdrop) backdrop.addEventListener("click", closeDrawer);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && drawer && drawer.classList.contains("open")) {
      closeDrawer();
    }
  });

  document.querySelectorAll(".drawer-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.getAttribute("data-drawer-tab");
      switchDrawerTab(target);
    });
  });

  const btnRunTwinRehearsal = document.getElementById("btnRunTwinRehearsal");
  if (btnRunTwinRehearsal) {
    btnRunTwinRehearsal.addEventListener("click", () => {
      switchView("view-future-rehearsal");
      runFutureRehearsal();
    });
  }

  const btnSimulate = document.getElementById("btnSimulateIntervention");
  if (btnSimulate) {
    btnSimulate.addEventListener("click", () => {
      openDrawer("tab-hazards");
    });
  }
}

function switchDrawerTab(tabId) {
  document.querySelectorAll(".drawer-tab").forEach(t => {
    if (t.getAttribute("data-drawer-tab") === tabId) {
      t.classList.add("active");
    } else {
      t.classList.remove("active");
    }
  });

  document.querySelectorAll(".drawer-pane").forEach(p => {
    if (p.id === tabId) {
      p.classList.add("active");
    } else {
      p.classList.remove("active");
    }
  });
}
