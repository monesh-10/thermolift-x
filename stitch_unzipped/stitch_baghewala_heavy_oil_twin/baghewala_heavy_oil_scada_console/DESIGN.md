---
name: Baghewala Heavy Oil SCADA Console
colors:
  surface: '#fcf9f4'
  surface-dim: '#dcdad5'
  surface-bright: '#fcf9f4'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3ee'
  surface-container: '#f0ede9'
  surface-container-high: '#ebe8e3'
  surface-container-highest: '#e5e2dd'
  on-surface: '#1c1c19'
  on-surface-variant: '#4e4541'
  inverse-surface: '#31302d'
  inverse-on-surface: '#f3f0eb'
  outline: '#7f7570'
  outline-variant: '#d1c4be'
  surface-tint: '#665d58'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#211a17'
  on-primary-container: '#8c827d'
  inverse-primary: '#d0c4bf'
  secondary: '#246a4c'
  on-secondary: '#ffffff'
  secondary-container: '#a8efc8'
  on-secondary-container: '#296f50'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#2d1600'
  on-tertiary-container: '#bd721d'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ede0da'
  primary-fixed-dim: '#d0c4bf'
  on-primary-fixed: '#211a17'
  on-primary-fixed-variant: '#4d4541'
  secondary-fixed: '#abf2cb'
  secondary-fixed-dim: '#8fd5b0'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005235'
  tertiary-fixed: '#ffdcbf'
  tertiary-fixed-dim: '#ffb874'
  on-tertiary-fixed: '#2d1600'
  on-tertiary-fixed-variant: '#6b3b00'
  background: '#fcf9f4'
  on-background: '#1c1c19'
  surface-variant: '#e5e2dd'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 38px
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 30px
  headline-md:
    fontFamily: Inter
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
    lineHeight: 15px
  telemetry-display:
    fontFamily: JetBrains Mono
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 32px
  telemetry-lg:
    fontFamily: JetBrains Mono
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 22px
  telemetry-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
  telemetry-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 14px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 12px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 0.75rem
  margin: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style
The design system delivers an austere, mission-critical Swiss Industrial aesthetic calibrated for field engineers, control room operators, and petroleum technicians at the Baghewala Heavy Oil Field (SIH 26120). It fuses the informational discipline of mid-century Swiss graphic design with modern SCADA high-density operational telemetry. 

The visual tone is clinical, decisive, and grounded. It prioritizes instantaneous pattern recognition under high cognitive load, completely omitting decorative gradients, glassmorphism, or non-functional visual ornamentation. Data interfaces operate as precision machinery: rigid modular alignment, explicit boundary rules, disciplined typographic cadence, and deterministic functional color coding.

## Colors
The palette balances environmental comfort in low-to-high ambient control room lighting against high-contrast semantic acuity.

- **Primary Canvas & Surfaces**:
  - Global Canvas: Porcelain Sand (`#FAF7F2`) provides a glare-resistant, warm tactile ground.
  - Surface Card / Container: Crisp Technical White (`#FFFFFF`).
  - Structural Borders & Grid Lines: Muted Bone Sand (`#E8E2D8`).
  - High-Density Chrome & Banners: Deep Espresso Charcoal (`#1B1512`) used for master workstation header bars, alert ribbons, and telemetry badges to enforce grounding contrast.

- **Functional SCADA Accents**:
  - **Petroleum Sage Green (`#286E4F`)**: Nominal operating status, optimal pump fillage (>85%), active cyclic steam injection validation.
  - **Thermal Amber (`#B86E18`)**: Thermal/CSS alerts, temperature thresholds, non-critical deviation from baseline setpoints.
  - **Rust Crimson (`#B93838`)**: Rod floating alerts, parted rod strings, severe pressure drops, motor trip interlocks.
  - **Deep Slate Teal (`#3B6B88`)**: Hydraulic pressure circuits, secondary lifting mechanisms, auxiliary fluid transport circuits.
  - **Muted Steel (`#766E65`)**: Inactive metrics, structural grid ticks, secondary telemetry units, and disabled control states.

## Typography
Typography is split into structural information and dynamic machine telemetry:

- **Structural UI (Inter)**: Handles card titles, navigation taxonomies, module labels, and administrative instructions. Letter spacing is standard to slightly condensed for compact horizontal packaging.
- **Dynamic Telemetry & Setpoints (JetBrains Mono)**: Renders all live instrumentation (temperatures, strokes per minute, barometric pressure, API gravity, dynagraph card coordinates, wellhead PSI, and electrical loads). Tabular numbers are mandatory across all mono styles to prevent layout jitter during sub-second streaming updates.
- **Label-Caps Role**: Displayed with `text-transform: uppercase` and `letter-spacing: 0.08em` for unit badges, operational states, and field identifiers.

## Layout & Spacing
The layout adheres to a rigid, high-density 12-column grid system tuned for 1080p, 1440p, and multi-monitor SCADA console arrays.

- **Grid Architecture**: Standard horizontal gutters are `0.75rem` (12px), enabling maximal screen utilization with zero dead space. Canvas margins are locked to `1rem` (16px).
- **Rhythm**: Spacing follows an ultra-compact 4px modular base (`0.25rem`, `0.5rem`, `0.75rem`, `1rem`, `1.5rem`). Information density takes precedence over expansive whitespace.
- **Breakpoints**:
  - `Desktop Wide` (≥1680px): Full 12-column dashboard layout with persistent 3-column well-string telemetry panel, 6-column center dynagraph/CSS visualization, and 3-column alert matrix.
  - `Workstation Standard` (1280px - 1679px): 12 columns, secondary telemetry modules collapse into switchable tabs.
  - `Field Tablet` (<1280px): 6 columns, sequential single-column card stacking with persistent pinned top-level emergency bar.

## Elevation & Depth
Elevation is achieved exclusively through technical planar stacking and 1px structural boundaries. Diffused ambient shadows and skeuomorphic drop shadows are prohibited to prevent visual smear in high-density data matrices.

- **Base Ground**: Surface tint `#FAF7F2`.
- **Level 1 (Cards & Data Cells)**: Crisp `#FFFFFF` surface bounded by a continuous 1px `#E8E2D8` hairline border.
- **Level 2 (Active Controls / Popovers / Flyouts)**: Surface `#FFFFFF` encased in a 1px `#1B1512` boundary with a crisp, non-diffused 2px technical offset (`box-shadow: 2px 2px 0px rgba(27, 21, 18, 0.12)`).
- **Inverted Surfaces (Chrome Banners / Terminal Bars)**: Grounded `#1B1512` solid fill with inset 1px dividers of `#332A24`.

## Shapes
Shapes express the machine-tooled precision of physical industrial hardware. 

- All primary modules, cards, telemetry boxes, and action surfaces utilize a uniform 2px to 4px radius corner (`roundedness: 1`).
- Status indicator tags, setpoint input fields, and dynagraph coordinate enclosures maintain tight, razor-sharp 2px corners.
- Pill shapes, circular avatars, and irregular organic cuts are forbidden.

## Components

### Buttons & Action Controls
- **Primary Operational Button**: Background `#1B1512`, text `#FFFFFF`, 1px solid `#1B1512` border, 2px border radius. Font: `JetBrains Mono`, 12px, weight 500, uppercase.
- **Secondary / Setpoint Trigger**: Background `#FFFFFF`, text `#1B1512`, 1px solid `#E8E2D8` border. Hover: border `#1B1512`.
- **Critical Interlock Button (ESD / Wellhead Shut-In)**: Background `#B93838`, text `#FFFFFF`, 1px solid `#8D2222`. Active state triggers high-contrast hatched border.

### Telemetry Badges & Status Chips
- Height is fixed at 20px or 24px. Border-radius is 2px.
- **Nominal State**: Background `#EAF2ED`, border `#286E4F`, text `#286E4F`.
- **Thermal Alert**: Background `#F9F2E7`, border `#B86E18`, text `#B86E18`.
- **Critical / Rod Float**: Background `#F9EBEB`, border `#B93838`, text `#B93838`.
- Content pattern: JetBrains Mono text accompanied by a 6px square indicator block.

### Cards & Telemetry Tiles
- Structured with `#FFFFFF` background, 1px `#E8E2D8` border, and 12px interior padding (`space-md`).
- Header tier: Separated from the card body by a 1px solid `#E8E2D8` hairline divider, featuring uppercase Inter metadata labels on the left and JetBrains Mono well IDs on the right.

### Input Fields & Setpoint Steppers
- Height is locked at 28px. Background is `#FAF7F2` with a 1px `#E8E2D8` frame.
- Text is right-aligned in `JetBrains Mono` with fixed unit indicators (`m³/d`, `kN`, `°C`, `kPa`) anchored on the right in `#766E65`.
- Focus state: 1px outline of `#1B1512` with zero halo or glow blur.

### Checkboxes & Toggle Switches
- Checkboxes: 14x14px square, 1px `#1B1512` border, `#FFFFFF` interior. Checked state uses an exact solid `#1B1512` 8x8px square fill.
- SCADA Two-Position Interlocks: Mechanical slider box with a 1px border. Sliding toggles utilize hard mechanical snaps with zero ease-in damping.

### Domain-Specific Components
- **Dynagraph Card Plotter Container**: White card with a 1px `#E8E2D8` boundary enclosing an inner plotting grid aligned to 10kN load (Y-axis) and 200mm stroke position (X-axis). Surface load plots render as a 1.5px solid `#1B1512` polyline; downhole pump fillage renders in `#286E4F`.
- **Cyclic Steam Injection (CSS) Thermal Monitor**: Segmented horizontal gauge dividing zone temperatures with 1px `#E8E2D8` vertical tick lines, current steam pressure rendered in `telemetry-display` font.