/**
 * High-Tech Interactive Canvas Charts
 * 1. ThermalDeclineChart: Plots temperature decline curve vs viscosity surge and rod floating threshold.
 * 2. ProductionTimelineChart: Plots daily oil rate, water rate, and SPM over time.
 */

class ThermalDeclineChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.series = [];
    this.criticalVisc = 1250.0;
    this.currentDay = 45;

    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = 200 * window.devicePixelRatio;
    this.canvas.style.height = '200px';
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.render();
  }

  setData(simulationData, currentDay = 45) {
    this.series = simulationData.simulation_series || [];
    this.criticalVisc = simulationData.critical_viscosity_threshold_cp || 1250.0;
    this.currentDay = currentDay;
    this.render();
  }

  render() {
    const ctx = this.ctx;
    const w = this.canvas.width / window.devicePixelRatio;
    const h = 200;

    ctx.clearRect(0, 0, w, h);
    if (this.series.length === 0) return;

    const padLeft = 40;
    const padRight = 45;
    const padTop = 20;
    const padBottom = 25;

    const plotW = w - padLeft - padRight;
    const plotH = h - padTop - padBottom;

    const maxDay = 120;
    const minTemp = 40, maxTemp = 200;
    const minVisc = 0, maxVisc = 5000;

    const toX = day => padLeft + (day / maxDay) * plotW;
    const toYTemp = t => padTop + plotH - ((t - minTemp) / (maxTemp - minTemp)) * plotH;
    const toYVisc = v => padTop + plotH - ((v - minVisc) / (maxVisc - minVisc)) * plotH;

    // Grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let day = 0; day <= maxDay; day += 20) {
      const gx = toX(day);
      ctx.beginPath();
      ctx.moveTo(gx, padTop);
      ctx.lineTo(gx, padTop + plotH);
      ctx.stroke();
      ctx.font = '8px "JetBrains Mono", monospace';
      ctx.fillStyle = '#64748b';
      ctx.fillText(`D${day}`, gx - 8, padTop + plotH + 14);
    }

    // Critical Rod Floating Threshold Band (> 1,250 cP)
    const critY = toYVisc(this.criticalVisc);
    ctx.fillStyle = 'rgba(239, 68, 68, 0.08)';
    ctx.fillRect(padLeft, padTop, plotW, critY - padTop);

    ctx.setLineDash([3, 3]);
    ctx.strokeStyle = 'rgba(239, 68, 68, 0.5)';
    ctx.beginPath();
    ctx.moveTo(padLeft, critY);
    ctx.lineTo(padLeft + plotW, critY);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.font = '8px "JetBrains Mono", monospace';
    ctx.fillStyle = '#f87171';
    ctx.fillText('CRITICAL VISCOSITY THRESHOLD (ROD FLOATING ONSET)', padLeft + 10, critY - 4);

    // 1. Plot Temperature Decline Curve (Orange/Amber)
    ctx.strokeStyle = '#f59e0b';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(toX(this.series[0].day), toYTemp(this.series[0].temperature_c));
    for (let i = 1; i < this.series.length; i++) {
      ctx.lineTo(toX(this.series[i].day), toYTemp(this.series[i].temperature_c));
    }
    ctx.stroke();

    // 2. Plot Viscosity Surge Curve (Purple / Pink)
    ctx.strokeStyle = '#a855f7';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(toX(this.series[0].day), toYVisc(this.series[0].viscosity_cp));
    for (let i = 1; i < this.series.length; i++) {
      ctx.lineTo(toX(this.series[i].day), toYVisc(this.series[i].viscosity_cp));
    }
    ctx.stroke();

    // Current Day Cursor
    const currX = toX(this.currentDay);
    ctx.strokeStyle = '#00f2fe';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(currX, padTop);
    ctx.lineTo(currX, padTop + plotH);
    ctx.stroke();

    ctx.fillStyle = '#00f2fe';
    ctx.fillText(`CURRENT DAY ${this.currentDay}`, currX - 35, padTop - 6);

    // Chart Legends
    ctx.font = '9px "Outfit", sans-serif';
    ctx.fillStyle = '#f59e0b';
    ctx.fillRect(padLeft + 10, h - 8, 10, 3);
    ctx.fillText('Reservoir Temp (°C)', padLeft + 24, h - 5);

    ctx.fillStyle = '#a855f7';
    ctx.fillRect(padLeft + 150, h - 8, 10, 3);
    ctx.fillText('Oil Viscosity (cP)', padLeft + 164, h - 5);
  }
}

class ProductionTimelineChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.timelineData = [];

    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = 180 * window.devicePixelRatio;
    this.canvas.style.height = '180px';
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.render();
  }

  setData(timelineData) {
    this.timelineData = timelineData || [];
    this.render();
  }

  render() {
    const ctx = this.ctx;
    const w = this.canvas.width / window.devicePixelRatio;
    const h = 180;

    ctx.clearRect(0, 0, w, h);
    if (this.timelineData.length === 0) return;

    const padLeft = 40;
    const padRight = 20;
    const padTop = 15;
    const padBottom = 25;

    const plotW = w - padLeft - padRight;
    const plotH = h - padTop - padBottom;

    const n = this.timelineData.length;
    const maxRate = Math.max(...this.timelineData.map(d => Math.max(d.oil_rate_bopd, d.water_rate_bwpd)), 80.0) * 1.15;

    const toX = idx => padLeft + (idx / (n - 1)) * plotW;
    const toY = rate => padTop + plotH - (rate / maxRate) * plotH;

    // Grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
    ctx.lineWidth = 1;
    for (let r = 0; r <= maxRate; r += 20) {
      const gy = toY(r);
      ctx.beginPath();
      ctx.moveTo(padLeft, gy);
      ctx.lineTo(padLeft + plotW, gy);
      ctx.stroke();
      ctx.font = '8px "JetBrains Mono", monospace';
      ctx.fillStyle = '#64748b';
      ctx.fillText(`${r}`, padLeft - 22, gy + 3);
    }

    // 1. Water Rate Line (Blue)
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(toX(0), toY(this.timelineData[0].water_rate_bwpd));
    for (let i = 1; i < n; i++) {
      ctx.lineTo(toX(i), toY(this.timelineData[i].water_rate_bwpd));
    }
    ctx.stroke();

    // 2. Oil Rate Line (Emerald Green)
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(toX(0), toY(this.timelineData[0].oil_rate_bopd));
    for (let i = 1; i < n; i++) {
      ctx.lineTo(toX(i), toY(this.timelineData[i].oil_rate_bopd));
    }
    ctx.stroke();

    // Highlight Rod Floating Incident points in Red
    this.timelineData.forEach((d, idx) => {
      if (d.rod_floating) {
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(toX(idx), toY(d.oil_rate_bopd), 3.5, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    // Legends
    ctx.font = '9px "Outfit", sans-serif';
    ctx.fillStyle = '#10b981';
    ctx.fillRect(padLeft + 10, h - 8, 10, 3);
    ctx.fillText('Oil Production (bopd)', padLeft + 24, h - 5);

    ctx.fillStyle = '#3b82f6';
    ctx.fillRect(padLeft + 140, h - 8, 10, 3);
    ctx.fillText('Water Production (bwpd)', padLeft + 154, h - 5);

    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(padLeft + 285, h - 6, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillText('Rod Floating Incident', padLeft + 293, h - 5);
  }
}
