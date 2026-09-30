/**
 * Rig & Wellbore Canvas Renderer
 * Renders an animated, high-fidelity mechanical and thermal cross-section of the
 * Sucker Rod Pump (SRP) system, sucker rod string stress, and reservoir thermal zone.
 */

class RigRenderer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    
    // Animation state
    this.spm = 8.0;
    this.strokeLengthIn = 100.0;
    this.fillagePct = 80.0;
    this.isRodFloating = false;
    this.floatingMarginPct = 25.0;
    this.tempC = 65.0;
    this.theta = 0; // Crank angle
    this.lastTime = performance.now();
    this.bubbles = [];

    // Initialize random fluid bubbles rising up tubing
    for (let i = 0; i < 25; i++) {
      this.bubbles.push({
        y: Math.random() * 260 + 120,
        xOffset: (Math.random() - 0.5) * 12,
        speed: Math.random() * 0.8 + 0.4,
        size: Math.random() * 2 + 1.5
      });
    }

    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  resizeCanvas() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = 420 * window.devicePixelRatio;
    this.canvas.style.height = '420px';
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }

  updateState(wellState) {
    if (!wellState) return;
    this.spm = wellState.surface_srp?.spm || 8.0;
    this.strokeLengthIn = wellState.surface_srp?.stroke_length_in || 100.0;
    this.fillagePct = wellState.surface_srp?.fillage_pct || 80.0;
    this.isRodFloating = wellState.mechanics?.is_rod_floating || false;
    this.floatingMarginPct = wellState.mechanics?.floating_margin_pct || 25.0;
    this.tempC = wellState.reservoir?.temperature_c || 65.0;
  }

  animate(currentTime) {
    const dt = (currentTime - this.lastTime) / 1000.0;
    this.lastTime = currentTime;

    // Angular velocity: omega = 2 * pi * (spm / 60)
    const omega = 2.0 * Math.PI * (this.spm / 60.0);
    this.theta = (this.theta + omega * dt) % (2.0 * Math.PI);

    this.render();
    requestAnimationFrame(this.animate);
  }

  render() {
    const ctx = this.ctx;
    const w = this.canvas.width / window.devicePixelRatio;
    const h = 420;

    ctx.clearRect(0, 0, w, h);

    // Background Grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 30) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 30) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // Kinematic stroke displacement: y = (stroke / 2) * (1 - cos(theta))
    // Normalized 0 to 1
    const normDisp = (1.0 - Math.cos(this.theta)) / 2.0;
    const strokePixelMax = 28; // visual pixel travel
    const rodYOffset = normDisp * strokePixelMax;

    // ==========================================
    // 1. SURFACE PUMPING UNIT (Top Left / Center)
    // ==========================================
    const groundY = 110;
    const wellheadX = w * 0.72;

    // Ground Line
    ctx.strokeStyle = 'rgba(100, 116, 139, 0.4)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(10, groundY);
    ctx.lineTo(w - 10, groundY);
    ctx.stroke();

    // Samson Post (A-Frame)
    const samsonBaseX = w * 0.35;
    const samsonTopX = w * 0.35;
    const samsonTopY = 38;

    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(samsonBaseX - 35, groundY);
    ctx.lineTo(samsonTopX, samsonTopY);
    ctx.lineTo(samsonBaseX + 35, groundY);
    ctx.stroke();

    // Walking Beam (Rocks back and forth)
    // Beam angle depends on stroke
    const beamAngle = (normDisp - 0.5) * 0.16;
    ctx.save();
    ctx.translate(samsonTopX, samsonTopY);
    ctx.rotate(beamAngle);

    // Draw Beam Body
    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2;
    ctx.fillRect(-70, -6, 140, 12);
    ctx.strokeRect(-70, -6, 140, 12);

    // Horsehead (Front Curved Head at wellhead side)
    ctx.fillStyle = '#0f172a';
    ctx.beginPath();
    ctx.arc(70, -12, 28, 0.2, Math.PI * 0.6);
    ctx.lineTo(70, 6);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Counterweight at rear
    ctx.fillStyle = '#64748b';
    ctx.fillRect(-68, -14, 25, 28);

    ctx.restore();

    // Bridle Wire Cables hanging from Horsehead to Carrier Bar
    const horseheadTipX = wellheadX;
    const horseheadTipY = samsonTopY - Math.sin(beamAngle) * 70 - 4;
    const carrierBarY = groundY - 25 + rodYOffset;

    ctx.strokeStyle = this.isRodFloating ? '#ef4444' : '#00f2fe';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(horseheadTipX - 4, horseheadTipY);
    // If rod is floating, cables show slack wave!
    if (this.isRodFloating && Math.sin(this.theta) < 0) {
      // Slack wire curve
      ctx.quadraticCurveTo(horseheadTipX - 10, (horseheadTipY + carrierBarY) / 2, horseheadTipX - 4, carrierBarY);
      ctx.moveTo(horseheadTipX + 4, horseheadTipY);
      ctx.quadraticCurveTo(horseheadTipX + 10, (horseheadTipY + carrierBarY) / 2, horseheadTipX + 4, carrierBarY);
    } else {
      ctx.lineTo(horseheadTipX - 4, carrierBarY);
      ctx.moveTo(horseheadTipX + 4, horseheadTipY);
      ctx.lineTo(horseheadTipX + 4, carrierBarY);
    }
    ctx.stroke();

    // Polished Rod Carrier Bar
    ctx.fillStyle = '#f8fafc';
    ctx.fillRect(wellheadX - 12, carrierBarY, 24, 6);

    // ==========================================
    // 2. WELLHEAD & STUFFING BOX
    // ==========================================
    ctx.fillStyle = '#334155';
    ctx.fillRect(wellheadX - 16, groundY - 14, 32, 14); // Stuffing box
    ctx.strokeStyle = '#00f2fe';
    ctx.strokeRect(wellheadX - 16, groundY - 14, 32, 14);

    // ==========================================
    // 3. WELLBORE CROSS-SECTION (Depth 0 to 1050m)
    // ==========================================
    const wellTopY = groundY;
    const wellBottomY = h - 20;
    const casingWidth = 54;
    const tubingWidth = 26;

    // Outer Casing (Grey Steel with Perforations at bottom)
    ctx.fillStyle = '#090d18';
    ctx.fillRect(wellheadX - casingWidth / 2, wellTopY, casingWidth, wellBottomY - wellTopY);
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 2;
    ctx.strokeRect(wellheadX - casingWidth / 2, wellTopY, casingWidth, wellBottomY - wellTopY);

    // Perforations at bottom (Reservoir Jodhpur Sandstone zone)
    const perfY = wellBottomY - 65;
    ctx.fillStyle = '#f59e0b';
    for (let py = perfY; py < wellBottomY - 10; py += 10) {
      // Left perforations
      ctx.fillRect(wellheadX - casingWidth / 2 - 4, py, 5, 2);
      // Right perforations
      ctx.fillRect(wellheadX + casingWidth / 2 - 1, py, 5, 2);
    }

    // Thermal Heat Map Glow at Reservoir (CSS Steam Zone)
    // Red/orange if hot (>100C), transitioning to cyan/slate if cooled (<60C)
    const heatFrac = Math.min(1.0, Math.max(0.0, (this.tempC - 48.0) / 120.0));
    const heatColor = heatFrac > 0.5 
      ? `rgba(239, 68, 68, ${0.15 + heatFrac * 0.3})`
      : `rgba(245, 158, 11, ${0.1 + heatFrac * 0.2})`;

    const heatGrad = ctx.createRadialGradient(wellheadX, perfY + 25, 10, wellheadX, perfY + 25, 90);
    heatGrad.addColorStop(0, heatColor);
    heatGrad.addColorStop(1, 'transparent');
    ctx.fillStyle = heatGrad;
    ctx.fillRect(wellheadX - 90, perfY - 30, 180, 110);

    // Inner Tubing
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(wellheadX - tubingWidth / 2, wellTopY, tubingWidth, perfY - wellTopY + 20);
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 1.5;
    ctx.strokeRect(wellheadX - tubingWidth / 2, wellTopY, tubingWidth, perfY - wellTopY + 20);

    // Heavy Oil Fluid in Annulus & Tubing
    ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
    ctx.fillRect(wellheadX - tubingWidth / 2 + 1, wellTopY + 1, tubingWidth - 2, perfY - wellTopY + 18);

    // Rising Oil Droplets / Bubbles in Tubing
    ctx.fillStyle = '#f59e0b';
    this.bubbles.forEach(b => {
      b.y -= b.speed * (this.spm / 8.0);
      if (b.y < wellTopY + 10) b.y = perfY;
      ctx.beginPath();
      ctx.arc(wellheadX + b.xOffset, b.y, b.size, 0, Math.PI * 2);
      ctx.fill();
    });

    // ==========================================
    // 4. SUCKER ROD STRING & STRESS COLORING
    // ==========================================
    const rodTopY = carrierBarY + 6;
    const pumpPlungerY = perfY - 15 + rodYOffset;

    // Sucker Rod Color based on stress & floating
    let rodColor = '#10b981'; // Green: healthy
    if (this.isRodFloating) {
      rodColor = '#ef4444'; // Red: Critical Slack & Impact Shock
    } else if (this.floatingMarginPct < 20.0) {
      rodColor = '#f59e0b'; // Amber: High viscous drag
    }

    ctx.strokeStyle = rodColor;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(wellheadX, rodTopY);
    ctx.lineTo(wellheadX, pumpPlungerY);
    ctx.stroke();

    // Polished Rod Glow
    ctx.shadowColor = rodColor;
    ctx.shadowBlur = this.isRodFloating ? 15 : 5;
    ctx.stroke();
    ctx.shadowBlur = 0; // reset

    // Downhole Pump Barrel & Traveling Valve
    const barrelY = perfY - 25;
    const barrelH = 45;

    // Pump Barrel Housing
    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 2;
    ctx.fillRect(wellheadX - 10, barrelY, 20, barrelH);
    ctx.strokeRect(wellheadX - 10, barrelY, 20, barrelH);

    // Plunger (Moves with rod)
    ctx.fillStyle = rodColor;
    ctx.fillRect(wellheadX - 8, pumpPlungerY, 16, 12);

    // Traveling Valve Ball
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(wellheadX, pumpPlungerY + 6, 2.5, 0, Math.PI * 2);
    ctx.fill();

    // Standing Valve at Bottom of Barrel
    ctx.fillStyle = '#64748b';
    ctx.fillRect(wellheadX - 8, barrelY + barrelH - 6, 16, 6);
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(wellheadX, barrelY + barrelH - 3, 2.5, 0, Math.PI * 2);
    ctx.fill();

    // ==========================================
    // 5. HUD TELEMETRY OVERLAYS ON CANVAS
    // ==========================================
    ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.2)';
    ctx.lineWidth = 1;
    ctx.fillRect(15, 15, 175, 75);
    ctx.strokeRect(15, 15, 175, 75);

    ctx.font = '10px "JetBrains Mono", monospace';
    ctx.fillStyle = '#94a3b8';
    ctx.fillText('DYNAMIC SRP KINEMATICS', 24, 30);

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 12px "JetBrains Mono", monospace';
    ctx.fillText(`STROKE: ${this.strokeLengthIn.toFixed(0)} in`, 24, 48);
    ctx.fillText(`SPEED : ${this.spm.toFixed(1)} SPM`, 24, 64);
    ctx.fillStyle = rodColor;
    ctx.fillText(this.isRodFloating ? 'STATUS: ROD FLOATING!' : `MARGIN: +${this.floatingMarginPct.toFixed(0)}%`, 24, 80);

    // Depth Markers on right
    ctx.font = '9px "JetBrains Mono", monospace';
    ctx.fillStyle = '#64748b';
    ctx.fillText('0 m (Surface)', wellheadX + casingWidth / 2 + 8, groundY + 12);
    ctx.fillText('500 m (Mid-String)', wellheadX + casingWidth / 2 + 8, (groundY + perfY) / 2);
    ctx.fillText('1000 m (Pump Depth)', wellheadX + casingWidth / 2 + 8, perfY + 10);
    ctx.fillStyle = '#f59e0b';
    ctx.fillText(`${this.tempC.toFixed(1)}°C (Jodhpur Sst)`, wellheadX + casingWidth / 2 + 8, perfY + 30);
  }
}
