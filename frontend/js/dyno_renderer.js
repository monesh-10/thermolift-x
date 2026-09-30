/**
 * Dynamometer Card Oscilloscope Renderer
 * Renders Surface Dynamometer Card (Polished Rod Load vs Position) and
 * Downhole Pump Card (Gibbs Card) with calibrated grids, load thresholds,
 * fluid pound notches, and rod floating anomaly markers.
 */

class DynoRenderer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    
    this.surfaceCard = [];
    this.downholeCard = [];
    this.pprl = 12.0;
    this.mprl = 3.5;
    this.strokeLength = 100.0;
    this.cardArea = 450.0;
    this.hasFluidPound = false;
    this.hasRodFloating = false;
    this.showDownhole = true;

    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = 290 * window.devicePixelRatio;
    this.canvas.style.height = '290px';
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.render();
  }

  updateData(dynoData) {
    if (!dynoData) return;
    this.surfaceCard = dynoData.surface_card || [];
    this.downholeCard = dynoData.downhole_card || [];
    this.pprl = dynoData.pprl_klb || 12.0;
    this.mprl = dynoData.mprl_klb || 3.5;
    this.strokeLength = dynoData.stroke_length_in || 100.0;
    this.cardArea = dynoData.card_area_klb_in || 450.0;
    this.hasFluidPound = dynoData.has_fluid_pound || false;
    this.hasRodFloating = dynoData.has_rod_floating || false;
    this.render();
  }

  render() {
    const ctx = this.ctx;
    const w = this.canvas.width / window.devicePixelRatio;
    const h = 290;

    ctx.clearRect(0, 0, w, h);

    // Coordinate transforms
    const padLeft = 45;
    const padRight = 20;
    const padTop = 25;
    const padBottom = 35;

    const plotW = w - padLeft - padRight;
    const plotH = h - padTop - padBottom;

    // Load Range: 0 to max(pprl * 1.25, 16 klb)
    const maxLoad = Math.max(16.0, this.pprl * 1.25);
    const maxStroke = Math.max(110.0, this.strokeLength * 1.1);

    const toX = pos => padLeft + (pos / maxStroke) * plotW;
    const toY = load => padTop + plotH - (load / maxLoad) * plotH;

    // 1. Draw Oscilloscope Grid
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.08)';
    ctx.lineWidth = 1;

    // Vertical grid lines (Stroke inches)
    ctx.font = '9px "JetBrains Mono", monospace';
    ctx.fillStyle = '#64748b';
    for (let strokeStep = 0; strokeStep <= maxStroke; strokeStep += 20) {
      const gx = toX(strokeStep);
      ctx.beginPath();
      ctx.moveTo(gx, padTop);
      ctx.lineTo(gx, padTop + plotH);
      ctx.stroke();
      ctx.fillText(`${strokeStep}"`, gx - 8, padTop + plotH + 15);
    }

    // Horizontal grid lines (Load klb)
    for (let loadStep = 0; loadStep <= maxLoad; loadStep += 4) {
      const gy = toY(loadStep);
      ctx.beginPath();
      ctx.moveTo(padLeft, gy);
      ctx.lineTo(padLeft + plotW, gy);
      ctx.stroke();
      ctx.fillText(`${loadStep}k`, padLeft - 28, gy + 3);
    }

    // Axes lines
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.3)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(padLeft, padTop);
    ctx.lineTo(padLeft, padTop + plotH);
    ctx.lineTo(padLeft + plotW, padTop + plotH);
    ctx.stroke();

    // PPRL & MPRL Threshold Guidelines
    ctx.setLineDash([4, 4]);
    ctx.strokeStyle = 'rgba(239, 68, 68, 0.45)'; // PPRL line
    ctx.beginPath();
    ctx.moveTo(padLeft, toY(this.pprl));
    ctx.lineTo(padLeft + plotW, toY(this.pprl));
    ctx.stroke();
    ctx.fillStyle = '#f87171';
    ctx.fillText(`PPRL: ${this.pprl.toFixed(1)}k`, padLeft + plotW - 65, toY(this.pprl) - 4);

    ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)'; // MPRL line
    ctx.beginPath();
    ctx.moveTo(padLeft, toY(this.mprl));
    ctx.lineTo(padLeft + plotW, toY(this.mprl));
    ctx.stroke();
    ctx.fillStyle = '#38bdf8';
    ctx.fillText(`MPRL: ${this.mprl.toFixed(1)}k`, padLeft + plotW - 65, toY(this.mprl) + 12);
    ctx.setLineDash([]); // Reset line dash

    // 2. Draw Downhole Pump Card (Gibbs Card) in Amber/Gold
    if (this.showDownhole && this.downholeCard.length > 2) {
      ctx.strokeStyle = '#f59e0b';
      ctx.fillStyle = 'rgba(245, 158, 11, 0.08)';
      ctx.lineWidth = 2;

      ctx.beginPath();
      const first = this.downholeCard[0];
      ctx.moveTo(toX(first.position_in), toY(first.load_klb));

      for (let i = 1; i < this.downholeCard.length; i++) {
        const pt = this.downholeCard[i];
        ctx.lineTo(toX(pt.position_in), toY(pt.load_klb));
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }

    // 3. Draw Surface Dynamometer Card in Neon Cyan
    if (this.surfaceCard.length > 2) {
      ctx.strokeStyle = this.hasRodFloating ? '#ff3366' : '#00f2fe';
      ctx.fillStyle = this.hasRodFloating ? 'rgba(255, 51, 102, 0.12)' : 'rgba(0, 242, 254, 0.12)';
      ctx.lineWidth = 2.5;

      // Card Glow
      ctx.shadowColor = this.hasRodFloating ? '#ff3366' : '#00f2fe';
      ctx.shadowBlur = 10;

      ctx.beginPath();
      const first = this.surfaceCard[0];
      ctx.moveTo(toX(first.position_in), toY(first.load_klb));

      for (let i = 1; i < this.surfaceCard.length; i++) {
        const pt = this.surfaceCard[i];
        ctx.lineTo(toX(pt.position_in), toY(pt.load_klb));
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      ctx.shadowBlur = 0; // reset
    }

    // 4. Highlight Anomalies on Card
    if (this.hasRodFloating) {
      // Draw alert badge on card
      ctx.fillStyle = 'rgba(239, 68, 68, 0.2)';
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 1;
      ctx.fillRect(padLeft + 15, padTop + 10, 150, 24);
      ctx.strokeRect(padLeft + 15, padTop + 10, 150, 24);

      ctx.font = 'bold 9px "JetBrains Mono", monospace';
      ctx.fillStyle = '#ef4444';
      ctx.fillText('⚠ SLACK & IMPACT NOTCH', padLeft + 22, padTop + 25);
    } else if (this.hasFluidPound) {
      ctx.fillStyle = 'rgba(245, 158, 11, 0.2)';
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 1;
      ctx.fillRect(padLeft + 15, padTop + 10, 140, 24);
      ctx.strokeRect(padLeft + 15, padTop + 10, 140, 24);

      ctx.font = 'bold 9px "JetBrains Mono", monospace';
      ctx.fillStyle = '#f59e0b';
      ctx.fillText('⚠ FLUID POUND NOTCH', padLeft + 22, padTop + 25);
    }

    // Card Legend
    ctx.font = '9px "Outfit", sans-serif';
    // Surface Legend
    ctx.fillStyle = this.hasRodFloating ? '#ff3366' : '#00f2fe';
    ctx.fillRect(padLeft + 10, h - 14, 12, 4);
    ctx.fillStyle = '#cbd5e1';
    ctx.fillText('Surface Card (Polished Rod)', padLeft + 26, h - 10);

    // Downhole Legend
    ctx.fillStyle = '#f59e0b';
    ctx.fillRect(padLeft + 180, h - 14, 12, 4);
    ctx.fillStyle = '#cbd5e1';
    ctx.fillText('Downhole Card (Gibbs Pump)', padLeft + 196, h - 10);
  }
}
