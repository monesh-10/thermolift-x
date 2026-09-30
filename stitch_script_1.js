
    // --- Global State Variables ---
    let simState = {
      spm: 6.9,
      temp: 68.7,
      viscosity: 2239,
      soakDays: 7.0,
      phase: 0,
      time: 0,
      fallMargin: 14.2,
      bopd: 8.8,
      hazard: 34.6,
      isPlayingReplay: false,
      replayInterval: null,
      currentReplayStep: 6
    };

    // --- DOM Elements ---
    const srpCanvas = document.getElementById('srpTwinCanvas');
    const srpCtx = srpCanvas.getContext('2d');
    const dynoCanvas = document.getElementById('dynoCardCanvas');
    const dynoCtx = dynoCanvas.getContext('2d');

    // --- Resize Canvases to Physical Display ---
    function resizeCanvases() {
      if (srpCanvas && dynoCanvas) {
        srpCanvas.width = srpCanvas.parentElement.clientWidth;
        srpCanvas.height = srpCanvas.parentElement.clientHeight;
        dynoCanvas.width = dynoCanvas.parentElement.clientWidth;
        dynoCanvas.height = dynoCanvas.parentElement.clientHeight;
      }
    }
    window.addEventListener('resize', resizeCanvases);
    window.addEventListener('DOMContentLoaded', () => {
      resizeCanvases();
      requestAnimationFrame(renderLoop);
    });

    // --- Real-Time Numerical Parameter Update ---
    function updateTunerVal(param, val, suffix) {
      val = parseFloat(val);
      if (param === 'spm') {
        simState.spm = val;
        document.getElementById('val-spm').innerText = val.toFixed(1) + suffix;
      } else if (param === 'temp') {
        simState.temp = val;
        document.getElementById('val-temp').innerText = val.toFixed(1) + suffix;
        // Coupler: temperature dramatically alters viscosity
        simState.viscosity = Math.round(50000 * Math.exp(-0.045 * val));
        document.getElementById('slider-viscosity').value = simState.viscosity;
        document.getElementById('val-viscosity').innerText = simState.viscosity.toLocaleString() + ' cP';
      } else if (param === 'viscosity') {
        simState.viscosity = val;
        document.getElementById('val-viscosity').innerText = Math.round(val).toLocaleString() + suffix;
      } else if (param === 'soak') {
        simState.soakDays = val;
        document.getElementById('val-soak').innerText = val.toFixed(1) + suffix;
      }
      recalculateDynamics();
    }

    // --- Recalculate Cyber-Physical Dynamics (Coupled Gibbs / Stokes) ---
    function recalculateDynamics() {
      // Stokes Annular Drag formula approximation
      const stokesFactor = (simState.viscosity / 1000) * (simState.spm / 6.0);
      const beamVelocity = (simState.spm * 2.5 * Math.PI) / 60; // m/s approx
      const rodTerminalVelocity = Math.max(0.4, 2.8 - (simState.viscosity / 1500));
      
      // Rod Fall Margin: positive is safe, <15% is warning, <=0 is severe buckle
      let calculatedMargin = ((rodTerminalVelocity - beamVelocity) / rodTerminalVelocity) * 100;
      calculatedMargin = Math.min(45, Math.max(-10, calculatedMargin));
      simState.fallMargin = calculatedMargin;

      // Update HUD and Readouts
      document.getElementById('hud-temp').innerText = simState.temp.toFixed(1);
      document.getElementById('hud-viscosity').innerText = Math.round(simState.viscosity).toLocaleString();
      document.getElementById('hud-fall-margin').innerText = (simState.fallMargin >= 0 ? '+' : '') + simState.fallMargin.toFixed(1) + '%';
      
      // Update Hazard % using Weibull model proxy
      simState.hazard = Math.min(99.9, Math.max(1.2, (simState.viscosity / 60) * (simState.spm / 5)));
      document.getElementById('hud-hazard').innerText = simState.hazard.toFixed(1) + '%';

      // Update BOPD proxy
      simState.bopd = Math.max(1.0, (simState.spm * 2.2) * (1 - simState.viscosity / 9000));
      document.getElementById('hud-bopd').innerText = simState.bopd.toFixed(1);

      // Dyn reads
      document.getElementById('dyn-stokes-drag').innerText = Math.round(1800 + stokesFactor * 1200) + ' N';
      document.getElementById('readout-fall-speed').innerText = rodTerminalVelocity.toFixed(2) + ' m/s';
      document.getElementById('readout-beam-speed').innerText = beamVelocity.toFixed(2) + ' m/s';
      
      const fallMarginLabel = document.getElementById('hud-fall-margin');
      const govFallMargin = document.getElementById('gov-fall-margin');
      if (simState.fallMargin < 15) {
        fallMarginLabel.className = 'font-label-numeric-lg text-label-numeric-lg text-tertiary font-bold';
        govFallMargin.className = 'font-label-numeric-sm text-label-numeric-sm text-tertiary font-bold';
        govFallMargin.innerText = simState.fallMargin.toFixed(1) + '% [MITIGATION REQ]';
      } else {
        fallMarginLabel.className = 'font-label-numeric-lg text-label-numeric-lg text-secondary font-bold';
        govFallMargin.className = 'font-label-numeric-sm text-label-numeric-sm text-secondary font-bold';
        govFallMargin.innerText = '+' + simState.fallMargin.toFixed(1) + '% [PASS]';
      }
    }

    // --- Horizon Selector ---
    function setHorizon(days) {
      [7, 14, 30].forEach(d => {
        const btn = document.getElementById('btn-hz-' + d);
        if (d === days) {
          btn.className = 'px-space-sm py-0.5 font-label-tag text-label-tag font-bold bg-primary text-surface-container-lowest';
        } else {
          btn.className = 'px-space-sm py-0.5 font-label-tag text-label-tag text-outline hover:text-on-surface';
        }
      });
    }

    // --- Apply Branch 6 Pareto Setpoint ---
    function applyBranch6() {
      document.getElementById('slider-spm').value = 4.8;
      updateTunerVal('spm', 4.8, ' SPM');
      openSignoffModal();
    }

    // --- Modal & Drawer Handlers ---
    function toggleSideDrawer() {
      const drawer = document.getElementById('fleetDrawer');
      drawer.classList.toggle('translate-x-full');
    }

    function openSignoffModal() {
      document.getElementById('signoffModal').classList.remove('hidden');
    }

    function closeSignoffModal() {
      document.getElementById('signoffModal').classList.add('hidden');
    }

    function executeSignoff() {
      const check = document.getElementById('auth-check');
      if (!check.checked) {
        alert("Please acknowledge the engineering sign-off checkbox before dispatch.");
        return;
      }
      closeSignoffModal();
      alert("IEC 61508 DISPATCH EXECUTED: Well BGW-002 VFD speed setpoint throttled to 4.8 SPM. Slack bridle cleared.");
      // Move to Replay Phase 12
      setReplayStep(12);
    }

    function triggerEstop() {
      if (confirm("EMERGENCY ESTOP TRIGGERED: Immediately de-energize surface motor contactor for BGW-002?")) {
        simState.spm = 0;
        document.getElementById('slider-spm').value = 0;
        updateTunerVal('spm', 0, ' SPM');
        alert("EMERGENCY ISOLATION COMPLETE. Well BGW-002 is held in zero-energy state.");
      }
    }

    function updateKnapsack(val) {
      document.getElementById('knapsack-cap').innerText = parseInt(val).toLocaleString() + ' m³';
    }

    function solveKnapsack() {
      alert("KNAPSACK RE-OPTIMIZATION COMPLETE: 8,500 m³ re-allocated across 16 wells. Maximum net gain: +84.2 BOPD with priority to BGW-002 thermal relief window.");
    }

    // --- 13-Phase Replay Stepper Logic ---
    const replayPhases = [
      "Phase 1: Initial cyclic steam injection soak period terminates. Formation temperature is 160°C.",
      "Phase 2: Well put on active artificial lift production at 6.9 SPM nominal design.",
      "Phase 3: Radial thermal dissipation begins; near-wellbore matrix drops from 140°C to 92°C.",
      "Phase 4: Viscosity rises non-linearly from 420 cP to 1,450 cP; annular shear friction triples.",
      "Phase 5: Downward terminal rod velocity falls below 1.4 m/s.",
      "Phase 6: Downhole drag exceeds polished rod weight; carrier bar separation velocity reaches 0.38 m/s.",
      "Phase 7: Severe bridle slack observed at top of stroke; shock loads spike to 4.2 klb on carrier catch.",
      "Phase 8: Gibbs wave PDE solver reconstructs downhole pump card exhibiting deep delayed stroke lag.",
      "Phase 9: 6-Branch Pareto engine performs counterfactual rehearsal over 7, 14, and 30-day horizons.",
      "Phase 10: SCADA Safety Governor trips interlock flag: Positive Fall Margin falls below 15% safety limit.",
      "Phase 11: Supervisory engineering alert dispatched to Oil India Limited central command room.",
      "Phase 12: Operator executes SIL-2 supervisory override: VFD setpoint smoothly throttled to 4.8 SPM.",
      "Phase 13: Positive fall margin recovers to +22.4%; slack bridle resolved; ₹38.2 Lakhs failure avoided."
    ];

    function setReplayStep(step) {
      simState.currentReplayStep = step;
      document.getElementById('replay-step-indicator').innerText = `PHASE ${step < 10 ? '0' + step : step} / 13`;
      document.getElementById('replay-caption').innerText = replayPhases[step - 1];

      for (let i = 1; i <= 13; i++) {
        const el = document.getElementById('p-step-' + i);
        if (el) {
          if (i === step) {
            el.className = 'p-1 border-2 border-primary bg-primary/20 text-primary font-bold';
          } else if (i < step) {
            el.className = 'p-1 border border-outline-variant bg-surface-container text-secondary font-medium';
          } else {
            el.className = 'p-1 border border-outline-variant bg-surface-container text-outline';
          }
        }
      }
    }

    function stepReplay(delta) {
      let next = simState.currentReplayStep + delta;
      if (next < 1) next = 1;
      if (next > 13) next = 13;
      setReplayStep(next);
    }

    function toggleReplayPlay() {
      const btn = document.getElementById('btn-replay-play');
      if (simState.isPlayingReplay) {
        clearInterval(simState.replayInterval);
        simState.isPlayingReplay = false;
        btn.innerText = 'PLAY';
        btn.className = 'px-space-sm py-0.5 bg-primary text-surface-container-lowest font-label-tag text-label-tag font-bold';
      } else {
        simState.isPlayingReplay = true;
        btn.innerText = 'PAUSE';
        btn.className = 'px-space-sm py-0.5 bg-tertiary text-surface-container-lowest font-label-tag text-label-tag font-bold';
        simState.replayInterval = setInterval(() => {
          let next = simState.currentReplayStep + 1;
          if (next > 13) next = 1;
          setReplayStep(next);
        }, 2400);
      }
    }

    function openReplayModal() {
      const el = document.getElementById('incident-replay');
      el.scrollIntoView({ behavior: 'smooth' });
    }

    // ==============================================================
    // MAIN CANVAS RENDERING LOOP (SRP DIGITAL TWIN + GIBBS DYNO)
    // ==============================================================
    function renderLoop(timestamp) {
      simState.time = timestamp * 0.001; // seconds

      // Angular velocity in radians/sec
      const omega = (simState.spm * 2 * Math.PI) / 60;
      const theta = simState.time * omega;

      // -------------------------------------------------------------
      // 1. RENDER LEFT SRP MECHANICAL TWIN
      // -------------------------------------------------------------
      if (srpCanvas && srpCtx) {
        const w = srpCanvas.width;
        const h = srpCanvas.height;
        srpCtx.clearRect(0, 0, w, h);

        // Technical Grid Background
        srpCtx.strokeStyle = '#141924';
        srpCtx.lineWidth = 1;
        for (let x = 0; x < w; x += 24) {
          srpCtx.beginPath();
          srpCtx.moveTo(x, 0);
          srpCtx.lineTo(x, h);
          srpCtx.stroke();
        }
        for (let y = 0; y < h; y += 24) {
          srpCtx.beginPath();
          srpCtx.moveTo(0, y);
          srpCtx.lineTo(w, y);
          srpCtx.stroke();
        }

        // Kinematics Geometry
        const groundY = 120;
        const samsonX = w * 0.35;
        const beamPivotY = 60;
        const beamLen = w * 0.28;
        
        // Beam Angle Oscillation
        const beamAngle = Math.sin(theta) * 0.18; // approx +/- 10 degrees

        // Crank & Pitman
        const crankPivotX = samsonX - beamLen * 0.75;
        const crankPivotY = groundY - 10;
        const crankRadius = 22;
        const crankX = crankPivotX + Math.cos(theta) * crankRadius;
        const crankY = crankPivotY + Math.sin(theta) * crankRadius;

        // Walking beam ends
        const horseheadX = samsonX + Math.cos(beamAngle) * beamLen;
        const horseheadY = beamPivotY - Math.sin(beamAngle) * beamLen;

        const tailX = samsonX - Math.cos(beamAngle) * (beamLen * 0.75);
        const tailY = beamPivotY + Math.sin(beamAngle) * (beamLen * 0.75);

        // Draw Samson Post (Base Tower)
        srpCtx.strokeStyle = '#2d384d';
        srpCtx.lineWidth = 3;
        srpCtx.beginPath();
        srpCtx.moveTo(samsonX - 25, groundY);
        srpCtx.lineTo(samsonX, beamPivotY);
        srpCtx.lineTo(samsonX + 25, groundY);
        srpCtx.stroke();

        // Cross braces on post
        srpCtx.strokeStyle = '#1a202c';
        srpCtx.lineWidth = 1.5;
        srpCtx.beginPath();
        srpCtx.moveTo(samsonX - 15, groundY - 25);
        srpCtx.lineTo(samsonX + 15, groundY - 45);
        srpCtx.moveTo(samsonX + 15, groundY - 25);
        srpCtx.lineTo(samsonX - 15, groundY - 45);
        srpCtx.stroke();

        // Draw Crank & Counterweight
        srpCtx.strokeStyle = '#3d494c';
        srpCtx.lineWidth = 4;
        srpCtx.beginPath();
        srpCtx.moveTo(crankPivotX, crankPivotY);
        srpCtx.lineTo(crankX, crankY);
        srpCtx.stroke();

        srpCtx.fillStyle = '#06b6d4';
        srpCtx.beginPath();
        srpCtx.arc(crankX, crankY, 6, 0, Math.PI * 2);
        srpCtx.fill();

        // Pitman Arm (connecting crank to beam tail)
        srpCtx.strokeStyle = '#869397';
        srpCtx.lineWidth = 2.5;
        srpCtx.beginPath();
        srpCtx.moveTo(crankX, crankY);
        srpCtx.lineTo(tailX, tailY);
        srpCtx.stroke();

        // Draw Walking Beam
        srpCtx.strokeStyle = '#4cd7f6';
        srpCtx.lineWidth = 6;
        srpCtx.beginPath();
        srpCtx.moveTo(tailX, tailY);
        srpCtx.lineTo(horseheadX, horseheadY);
        srpCtx.stroke();

        // Horsehead Curved Arc
        srpCtx.strokeStyle = '#06b6d4';
        srpCtx.lineWidth = 8;
        srpCtx.beginPath();
        srpCtx.arc(horseheadX - 10, horseheadY + 15, 25, -Math.PI * 0.3, Math.PI * 0.35);
        srpCtx.stroke();

        // Wellhead and Subsurface Casing
        const wellX = horseheadX + 14;
        const wellTopY = groundY - 10;
        
        // Wellhead Block (Christmas Tree)
        srpCtx.fillStyle = '#1c2028';
        srpCtx.strokeStyle = '#3d494c';
        srpCtx.lineWidth = 2;
        srpCtx.fillRect(wellX - 14, wellTopY, 28, 20);
        srpCtx.strokeRect(wellX - 14, wellTopY, 28, 20);

        // Ground Line
        srpCtx.strokeStyle = '#232b3b';
        srpCtx.lineWidth = 2;
        srpCtx.beginPath();
        srpCtx.moveTo(20, groundY + 10);
        srpCtx.lineTo(w - 20, groundY + 10);
        srpCtx.stroke();

        // Bridle Cable & Polished Rod Carrier Bar
        const strokePos = Math.sin(theta); // -1 (top) to +1 (bottom)
        const carrierY = wellTopY - 20 + (strokePos * 18);

        // Slack Bridle Visual Detection: if velocity down is high, cable curves
        const isDownstroke = Math.cos(theta) > 0;
        const isSlackRisk = isDownstroke && simState.fallMargin < 15;

        srpCtx.strokeStyle = isSlackRisk ? '#ef4444' : '#e2e8f0';
        srpCtx.lineWidth = 2;
        srpCtx.beginPath();
        if (isSlackRisk) {
          // Curved / slack cable
          srpCtx.moveTo(horseheadX + 14, horseheadY + 28);
          srpCtx.quadraticCurveTo(horseheadX + 24, (horseheadY + 28 + carrierY) / 2, wellX, carrierY);
        } else {
          srpCtx.moveTo(horseheadX + 14, horseheadY + 28);
          srpCtx.lineTo(wellX, carrierY);
        }
        srpCtx.stroke();

        // Carrier Bar
        srpCtx.fillStyle = isSlackRisk ? '#ef4444' : '#acedff';
        srpCtx.fillRect(wellX - 12, carrierY, 24, 4);

        // Wellbore Casing Downward Pipe (862m TVD representation)
        const wellBottomY = h - 25;
        srpCtx.strokeStyle = '#181c24';
        srpCtx.lineWidth = 18;
        srpCtx.beginPath();
        srpCtx.moveTo(wellX, wellTopY + 20);
        srpCtx.lineTo(wellX, wellBottomY);
        srpCtx.stroke();

        srpCtx.strokeStyle = '#232b3b';
        srpCtx.lineWidth = 1;
        srpCtx.strokeRect(wellX - 10, wellTopY + 20, 20, wellBottomY - wellTopY - 20);

        // Heavy Crude Annular Fluid Viscosity Gradient
        const crudeGrad = srpCtx.createLinearGradient(0, wellTopY + 20, 0, wellBottomY);
        crudeGrad.addColorStop(0, '#0a0e16');
        crudeGrad.addColorStop(0.7, '#1e293b');
        crudeGrad.addColorStop(1, '#ffb95f'); // Reservoir Thermal Plume
        srpCtx.fillStyle = crudeGrad;
        srpCtx.fillRect(wellX - 8, wellTopY + 20, 16, wellBottomY - wellTopY - 20);

        // Dynamic Sucker Rod String with Stress Gradient
        const rodLength = wellBottomY - carrierY - 25;
        const segCount = 18;
        const segH = rodLength / segCount;

        for (let i = 0; i < segCount; i++) {
          const segY = carrierY + 4 + i * segH;
          // Stress color: green (tension) vs amber vs red (compression/float)
          let segColor = '#4edea3';
          if (isSlackRisk && i < 6) {
            segColor = '#ef4444'; // Top segments in compression
          } else if (simState.viscosity > 1800) {
            segColor = '#ffb95f';
          }
          srpCtx.strokeStyle = segColor;
          srpCtx.lineWidth = 2.5;
          srpCtx.beginPath();
          srpCtx.moveTo(wellX, segY);
          srpCtx.lineTo(wellX, segY + segH - 1);
          srpCtx.stroke();
        }

        // Subsurface Pump Plunger & Standing Valve at Depth
        const pumpY = wellBottomY - 20 + (strokePos * 6);
        srpCtx.fillStyle = '#acedff';
        srpCtx.fillRect(wellX - 6, pumpY, 12, 16);

        // Perforations & Thermal Steam Ingress Effect
        srpCtx.fillStyle = '#ffb95f';
        for (let p = 0; p < 5; p++) {
          const py = wellBottomY - 30 + p * 6;
          srpCtx.fillRect(wellX - 15, py, 4, 2);
          srpCtx.fillRect(wellX + 11, py, 4, 2);
        }

        // Depth Marker
        srpCtx.fillStyle = '#64748b';
        srpCtx.font = '10px JetBrains Mono';
        srpCtx.fillText("862m TVD // BAGHEWALA PAY ZONE", wellX + 22, wellBottomY - 10);
      }

      // -------------------------------------------------------------
      // 2. RENDER RIGHT GIBBS DYNO OSCILLOSCOPE
      // -------------------------------------------------------------
      if (dynoCanvas && dynoCtx) {
        const dw = dynoCanvas.width;
        const dh = dynoCanvas.height;
        dynoCtx.clearRect(0, 0, dw, dh);

        // Oscilloscope Grid & Graticule
        dynoCtx.strokeStyle = '#141924';
        dynoCtx.lineWidth = 1;
        for (let x = 30; x < dw; x += 30) {
          dynoCtx.beginPath();
          dynoCtx.moveTo(x, 20);
          dynoCtx.lineTo(x, dh - 30);
          dynoCtx.stroke();
        }
        for (let y = 20; y < dh - 30; y += 30) {
          dynoCtx.beginPath();
          dynoCtx.moveTo(30, y);
          dynoCtx.lineTo(dw - 20, y);
          dynoCtx.stroke();
        }

        // Axis Lines
        dynoCtx.strokeStyle = '#2d384d';
        dynoCtx.lineWidth = 1.5;
        dynoCtx.beginPath();
        dynoCtx.moveTo(40, 20);
        dynoCtx.lineTo(40, dh - 30);
        dynoCtx.lineTo(dw - 20, dh - 30);
        dynoCtx.stroke();

        // Axis Labels
        dynoCtx.fillStyle = '#869397';
        dynoCtx.font = '9px JetBrains Mono';
        dynoCtx.fillText("LOAD (klb)", 10, 25);
        dynoCtx.fillText("0", 25, dh - 32);
        dynoCtx.fillText("10", 20, (dh - 30 + 30) / 2);
        dynoCtx.fillText("25", 20, 40);
        dynoCtx.fillText("STROKE POSITION (in)", dw * 0.45, dh - 12);

        // Graph Bounds
        const plotX = 50;
        const plotY = 35;
        const plotW = dw - 80;
        const plotH = dh - 80;

        // Surface Dyno Card (Polished Rod Load vs Stroke)
        // With heavy viscous drag: bottom slope drags upwards, top slope distorts
        const viscEffect = (simState.viscosity - 100) / 4000; // 0 to 2
        dynoCtx.strokeStyle = '#4cd7f6';
        dynoCtx.lineWidth = 2.5;
        dynoCtx.beginPath();

        const stepPts = 64;
        let tracerX = 0;
        let tracerY = 0;

        for (let i = 0; i <= stepPts; i++) {
          const a = (i / stepPts) * Math.PI * 2;
          // Parametric card shape
          const normPos = (1 + Math.sin(a)) / 2; // 0 to 1
          
          // Load formula with hysteresis & Stokes drag tail
          let load = 12 + Math.cos(a) * 7.5;
          if (Math.sin(a) > 0 && Math.cos(a) < 0) {
            // Downstroke drag bump (viscous rod float)
            load += viscEffect * 4.2;
          }
          if (a > Math.PI && a < Math.PI * 1.5) {
            // Fluid pound notch
            load -= 1.8;
          }

          const px = plotX + normPos * plotW;
          const py = plotY + plotH - (load / 26) * plotH;

          if (i === 0) dynoCtx.moveTo(px, py);
          else dynoCtx.lineTo(px, py);

          // Track current tracer point matching current time theta
          if (Math.abs(((theta % (Math.PI * 2)) - a)) < (Math.PI * 2 / stepPts)) {
            tracerX = px;
            tracerY = py;
          }
        }
        dynoCtx.closePath();
        dynoCtx.stroke();

        // Downhole Pump Card (Reconstructed via Gibbs Hyperbolic Wave PDE)
        // Shows delayed pump fillage, fluid pound, and severe stroke shortening
        dynoCtx.strokeStyle = '#4edea3';
        dynoCtx.lineWidth = 2;
        dynoCtx.setLineDash([4, 3]);
        dynoCtx.beginPath();

        const downholeFill = 0.81; // 81% fillage
        const pumpStrokeLoss = 0.18; // 18% loss due to rod stretch and rod float
        const pLeft = plotX + plotW * pumpStrokeLoss;
        const pRight = plotX + plotW * 0.95;
        const pBottom = plotY + plotH - (7.2 / 26) * plotH;
        const pTop = plotY + plotH - (18.6 / 26) * plotH;

        dynoCtx.moveTo(pLeft, pBottom);
        dynoCtx.lineTo(pRight, pBottom); // intake
        dynoCtx.lineTo(pRight, pTop);    // fluid transfer
        dynoCtx.lineTo(pLeft + (pRight - pLeft) * (1 - downholeFill), pTop); // discharge & gas exp
        dynoCtx.lineTo(pLeft, pBottom);
        dynoCtx.stroke();
        dynoCtx.setLineDash([]);

        // Active Tracer Dot on Surface Dyno Card
        if (tracerX > 0 && tracerY > 0) {
          dynoCtx.fillStyle = '#ffb95f';
          dynoCtx.beginPath();
          dynoCtx.arc(tracerX, tracerY, 5, 0, Math.PI * 2);
          dynoCtx.fill();
          dynoCtx.strokeStyle = '#0a0e16';
          dynoCtx.lineWidth = 1.5;
          dynoCtx.stroke();
        }
      }

      requestAnimationFrame(renderLoop);
    }
  