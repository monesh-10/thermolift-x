---
name: THERMOLIFT X Cyber-Physical Telemetry
colors:
  surface: '#0f131b'
  surface-dim: '#0f131b'
  surface-bright: '#353942'
  surface-container-lowest: '#0a0e16'
  surface-container-low: '#181c24'
  surface-container: '#1c2028'
  surface-container-high: '#262a33'
  surface-container-highest: '#31353e'
  on-surface: '#dfe2ee'
  on-surface-variant: '#bcc9cd'
  inverse-surface: '#dfe2ee'
  inverse-on-surface: '#2c3039'
  outline: '#869397'
  outline-variant: '#3d494c'
  surface-tint: '#4cd7f6'
  primary: '#4cd7f6'
  on-primary: '#003640'
  primary-container: '#06b6d4'
  on-primary-container: '#00424f'
  inverse-primary: '#00687a'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#e79400'
  on-tertiary-container: '#563400'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#acedff'
  primary-fixed-dim: '#4cd7f6'
  on-primary-fixed: '#001f26'
  on-primary-fixed-variant: '#004e5c'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0f131b'
  on-background: '#dfe2ee'
  surface-variant: '#31353e'
typography:
  headline-xl:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  body-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 16px
  label-numeric-lg:
    fontFamily: JetBrains Mono
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 30px
    letterSpacing: -0.02em
  label-numeric-md:
    fontFamily: JetBrains Mono
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 20px
  label-numeric-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-tag:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '700'
    lineHeight: 12px
    letterSpacing: 0.08em
spacing:
  gutter: 0.75rem
  gutter-desktop: 1rem
  margin: 1rem
  margin-desktop: 1.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

### Brand Personality & Mission
The design system powers an ultra-high-fidelity industrial cyber-physical SCADA console built specifically for heavy oil recovery operations (such as the Baghewala heavy oil reservoir under Oil India Limited). The operational environment demands relentless precision, zero cognitive friction, absolute situational awareness, and total engineering reliability. 

The aesthetic is grounded in aerospace-grade mission control and severe-duty petroleum telemetry: milled dark gunmetal, titanium chassis panels, chamfered steel bezels, and razor-sharp data readouts. It completely eschews decorative trends, whimsical radii, and cartoonish neon blurs. Visual weight is communicated through structural rigidity, micro-ruled divisions, high-density data instrumentation, and calibrated phosphor LED status signifiers.

### Target Audience & Psychological Intent
Engineered for reservoir engineers, telemetry specialists, automation technicians, and field dispatch operators working in safety-critical, 24/7 continuous operations. The interface instills calm, disciplined command under transient reservoir dynamics, thermal stimulation cycles, and downhole lift anomalies. High-contrast instrumentation ensures immediate legibility across ambient-lit control rooms and ruggedized field consoles.

## Colors

### Palette Philosophy
The palette simulates physical optical instrumentation against an anti-reflective dark titanium console chassis. Light emission is strictly reserved for actionable telemetry, valve states, and thermodynamic indicators.

- **Primary (`#06b6d4` Electric Cyan):** Dedicated to primary digital twin telemetry, dynamic operational vectors, pressure/viscosity flow paths, and focused sensor states.
- **Secondary (`#10b981` Emerald Phosphor):** Dedicated to nominal system performance, balanced thermal injection loops, stable wellhead pressure, and operational validation.
- **Tertiary (`#f59e0b` Amber Warning):** Dedicated to threshold limit warnings, transient steam breakthrough cautions, and localized cavitation alerts.
- **Safety Critical (`#ef4444` Safety Alert Crimson):** Dedicated to high-priority safety shutdowns, casing overpressure alerts, blowout preventer triggers, and emergency stop states.
- **Neutral Chassis Stack:**
  - Base Void: `#0b0e14` (Deepest milled bed)
  - Surface Panel: `#10141c` (Primary telemetry console chassis)
  - Raised Module: `#141924` (Sub-rack, HUD instrument containers)
  - Steel Milled Bevels: `#232b3b` (Structural inset borders)
  - Chamfer Highlight: `#2d384d` (Top-edge specular structural dividers)
  - Subdued Text / Data Legends: `#64748b`
  - Active Data Text: `#e2e8f0`
  - High-Luminance Instrumentation Readout: `#f8fafc`

## Typography

### Structural Role Assignment
- **Space Grotesk (Display & Structural Headers):** Delivers clean, modernist, architectural authority for rack module headers, asset designations (e.g., `BAGHEWALA-WELLHEAD-04`), and primary viewport anchors.
- **Inter (Synthesized Narrative & Descriptive Data):** Maximizes readability for configuration dialogs, diagnostic logs, alert descriptions, and procedural maintenance instructions.
- **JetBrains Mono (Numerical Telemetry & Hardware Metadata):** Strict monospaced alignment for real-time sensor metrics (cP, bar, °C, m³/d), downhole depth coordinates, IP/bus addresses, and status chips. Tabular numbers prevent jitter during dynamic data refresh cycles.

All uppercase tags utilize wide tracking (`0.08em`) to guarantee quick recognition on physical monitors and in peripheral vision.

## Layout & Spacing

### Modular Instrumentation Grid
The layout operates on a fluid, ultra-dense, 12-column sub-grid mapped to SCADA split-screen command consoles. Layouts adhere to a strict 4px micro-grid baseline:
- **Desktop (1440px and wider):** Multi-column HUD with a 1rem gutter and 1.5rem margins. Primary digital twin 3D schematic occupies a 7- or 8-column canvas, flanked by synchronized downhole sensor telemetry rails and valve control racks.
- **Tablet / Ruggedized Field Slates (768px - 1439px):** 6-column reflow where telemetry stacks horizontally beneath the primary isometric view; gutters collapse to 0.75rem, margins to 1rem.
- **Handheld Diagnostics (under 768px):** Single-column stacked telemetry feed with persistent bottom-pinned critical annunciator bar and quick-isolate safety overrides.

Interior component padding favors high density (`space-xs` and `space-sm`) to maximize visible real-time data points without requiring scrolling.

## Elevation & Depth

### Mechanical Milled Bevel Architecture
Depth is established mechanically via physical-layer milled steel offsets and contrasting border rails rather than ambient drop shadows:

1. **Recessed Sub-Bed (Elevation -1):**
   - Background: `#0b0e14`
   - Inset 1px border: `#1a202c`
   - Purpose: Graph plot areas, downhole wellbore cross-sections, and event log sinks.

2. **Console Chassis (Elevation 0):**
   - Background: `#10141c`
   - Purpose: Main viewport baseline canvas.

3. **Milled Instrument Modules (Elevation 1):**
   - Background: `#141924`
   - Borders: 1px continuous solid border `#232b3b` with a 1px top-highlight `#2d384d` to simulate a precision-machined chamfered bezel catching overhead illumination.
   - Purpose: Standard HUD cards, thermal telemetry modules, and parameter panels.

4. **Floating Overlays & Emergency Controls (Elevation 2):**
   - Background: `#182030`
   - Border: 1px `#3b475f` with a directional hard shadow `0 4px 12px rgba(0, 0, 0, 0.7)`.
   - Purpose: Valve manual override modals, sensor calibration overlays, and system emergency menus.

## Shapes

### Precision Machine-Cut Geometry
- **Level 0 (Sharp):** Radii throughout the entire design system are set to `0px`.
- Every panel, button, input field, tab, status lamp, and HUD chip exhibits pure perpendicular edges or 45-degree chamfered diagonal cuts on corner accents.
- This communicates mechanical rigidity, structural defense, and military-aerospace engineering specifications. Rounded, softened contours are systematically rejected.

## Components

### 1. Actuator Buttons & Physical-Style Toggles
- **Primary Cyber-Actuators:** `#06b6d4` background with `#0b0e14` bold monospaced typography. Borders are 1px `#22d3ee`. Hover states shift to an active electrical state with a 1px solid white perimeter rim. Active/press state triggers an instant 1px inner inset shadow (`inset 0 2px 4px rgba(0,0,0,0.8)`).
- **Secondary Machine Buttons:** Dark gunmetal `#141924` with a 1px `#232b3b` border, `#e2e8f0` text, and a top-edge 1px highlight of `#2d384d`.
- **Emergency / Isolation Buttons:** `#ef4444` base with high-contrast `#ffffff` monospaced text and diagonal hazard hash stripes (`45deg` alternating `#b91c1c` and `#ef4444`).

### 2. High-Density Telemetry Chips & Status Lamps
- **Phosphor LED Indicator Lamps:** 8x8px square indicators. Unlit state: `#1e293b`. Active state: `#10b981` (Nominal), `#f59e0b` (Transient Warning), or `#ef4444` (Critical Alarm) paired with a high-contrast 1px border. No diffuse blurred halos; indicator edges remain crisp and binary.
- **HUD Metric Chips:** Background `#0b0e14`, bordered by `#232b3b`. Contains micro tag label (`label-tag`) in `#64748b` top-aligned, and the live variable in `label-numeric-sm` right-aligned with the unit suffix (e.g., `48.2 cP`).

### 3. Precision Telemetry Data Tables & Lists
- Table headers utilize `#10141c` with all-caps `label-tag` text in `#64748b`, separated by a 1px solid `#232b3b` bottom rule.
- Alternating rows use subtle `#10141c` and `#141924` shading. Row hover states highlight the active data strip with a 1px vertical left-edge border of `#06b6d4`.
- All numeric readouts align right using `JetBrains Mono`.

### 4. Machine Inputs & Calibrated Sliders
- **Numerical Setpoint Inputs:** Stepper boxes styled as milled pockets (`#0b0e14`), with numerical text in `#f8fafc` and increment/decrement buttons integrated as discrete `#141924` square blocks with 1px `#232b3b` partitions.
- **Threshold Limiters / Range Sliders:** Track height 4px in `#1a202c`. Active range fill uses `#06b6d4`. The slider thumb is an 8x16px vertical rectangular block in `#e2e8f0` with three engraved vertical micro-grooves.

### 5. SCADA Instrumentation Cards & Digital Twin Viewports
- Modular frames enclosed by 1px `#232b3b` perimeter lines.
- Card titlebars feature an integrated left-aligned mechanical status pip, uppercase title in `Space Grotesk` (`headline-md`), and asset classification tags (e.g., `SEC-04 // INJECTION LOOP`) positioned on the upper-right flank.
- Integrated corner bracket markings (`+` crosshairs) to frame CAD wireframes, P&ID instrumentation schematics, and downhole thermal gradients.