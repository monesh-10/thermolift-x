# Physics & Fluid Mechanics Formulations (PINN-Twin™)

### 1. Andrade-Walther Viscosity Law for Baghewala Heavy Crude
$$\mu_{\text{oil}}(T) = \mu_{\text{ref}} \cdot \exp\left[\beta \cdot \left(\frac{1}{T + 273.15} - \frac{1}{T_{\text{ref}} + 273.15}\right)\right]$$
- $\beta = 3,800 \text{ K}$, $T_{\text{ref}} = 48.0^\circ\text{C}$, $\mu_{\text{ref}} = 3,800 \text{ cP}$.

### 2. Stokes-Navier Annular Drag & Rod Terminal Sinking Velocity
$$C_{\text{drag}} = \frac{2 \cdot \pi \cdot \mu_{\text{oil}} \cdot L}{\ln(d_t / d_r)}$$
$$W_{\text{buoyant}} = \left(\frac{\pi d_r^2}{4} L \rho_{\text{steel}}\right) g \left(1 - \frac{\rho_{\text{fluid}}}{\rho_{\text{steel}}}\right)$$
$$v_{\text{terminal}} = \frac{W_{\text{buoyant}}}{C_{\text{drag}}}$$

### 3. Surface Rod Kinematics & Floating Margin
$$v_{\text{PR, max}} = \pi \cdot S \cdot \frac{\text{SPM}}{60}$$
$$\text{Floating Margin \%} = \left(\frac{v_{\text{terminal}} - v_{\text{PR, max}}}{v_{\text{terminal}}}\right) \times 100\%$$

### 4. Slack Bridle Impact Shock Force on Upstroke Turnaround
$$\Delta v = \max(0, v_{\text{PR, max}} - v_{\text{terminal}})$$
$$E_{\text{impact}} = \frac{1}{2} M_{\text{rod}} (\Delta v)^2, \quad F_{\text{impact}} = \sqrt{2 E_{\text{impact}} k_{\text{rod}}}$$
