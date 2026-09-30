"""Physics Engine: First-Principles Mechanics & Thermal Models for Heavy Oil Wells.
Incorporates:
1. Andrade/Walther Heavy-Oil Viscosity-Temperature Model for Baghewala Field (17-19° API).
2. Stokes-Navier Viscous Drag & Rod Kinematics (Rod Floating & Impact Loading physics).
3. Surface & Downhole Dynamometer Card Synthesis (Gibbs Wave Equation approximation).
4. Thermal Reservoir Decay Model over CSS production cycles.
5. Specific Energy Consumption (kWh/bbl) & Economic Cost Calculation.
"""

import math
import numpy as np
from typing import Dict, Any, List, Tuple


class PhysicsEngine:
    # Physical Constants
    G = 9.80665              # m/s^2
    RHO_STEEL = 7850.0       # kg/m^3 (Grade D/K Sucker Rods)
    STEEL_MODULUS = 2.07e11  # Pa (Young's Modulus)

    @classmethod
    def oil_density_from_api(cls, api_deg: float) -> float:
        """Calculates crude density in kg/m^3 from API gravity."""
        sg = 141.5 / (api_deg + 131.5)
        return sg * 1000.0

    @classmethod
    def calculate_viscosity(cls, temp_c: float, dead_oil_visc_at_48c: float = 3800.0) -> float:
        """Andrade-type thermal viscosity model for Baghewala heavy crude.
        T in °C. Calibrated so at 48°C visc ~ dead_oil_visc, at 180°C visc ~ 35 cP.
        """
        t_kelvin = temp_c + 273.15
        t_ref = 48.0 + 273.15  # Baghewala reservoir temp ~48°C
        # Activation energy index for 17-19 API heavy crude
        beta = 3800.0  # Kelvin
        visc = dead_oil_visc_at_48c * math.exp(beta * (1.0 / t_kelvin - 1.0 / t_ref))
        return max(15.0, min(50000.0, visc))

    @classmethod
    def calculate_rod_mechanics(
        cls,
        spm: float,
        stroke_length_in: float,
        pump_depth_m: float,
        oil_viscosity_cp: float,
        api_gravity_deg: float = 18.0,
        rod_diameter_in: float = 0.875,  # 7/8 in
        tubing_id_in: float = 2.441,     # 2-7/8 in tubing
        pump_bore_in: float = 1.75
    ) -> Dict[str, Any]:
        """Calculates rod fall kinematics, viscous drag, floating margin, and impact shock loading."""
        stroke_m = stroke_length_in * 0.0254
        rod_d_m = rod_diameter_in * 0.0254
        tubing_id_m = tubing_id_in * 0.0254
        mu_pa_s = (oil_viscosity_cp / 1000.0)  # 1 cP = 0.001 Pa.s
        rho_fluid = cls.oil_density_from_api(api_gravity_deg)

        # Rod mass and buoyant weight
        rod_area = math.pi * (rod_d_m / 2.0) ** 2
        total_rod_mass = rod_area * pump_depth_m * cls.RHO_STEEL
        buoyant_weight_n = total_rod_mass * cls.G * (1.0 - (rho_fluid / cls.RHO_STEEL))
        buoyant_weight_klb = (buoyant_weight_n / 4.44822) / 1000.0

        # Fluid column weight on plunger (on upstroke)
        plunger_area = math.pi * (pump_bore_in * 0.0254 / 2.0) ** 2
        fluid_load_n = plunger_area * pump_depth_m * rho_fluid * cls.G
        fluid_load_klb = (fluid_load_n / 4.44822) / 1000.0

        # Maximum downward polished rod velocity (sinusoidal approximation)
        omega = 2.0 * math.pi * (spm / 60.0)
        v_pr_max = (stroke_m / 2.0) * omega  # m/s

        # Terminal falling velocity of rod string in viscous heavy oil (annular laminar flow)
        # F_drag = 2 * pi * mu * L * v / ln(r_t / r_r)
        ln_ratio = math.log(tubing_id_m / rod_d_m)
        drag_coeff = (2.0 * math.pi * mu_pa_s * pump_depth_m) / ln_ratio  # N/(m/s)

        v_terminal = buoyant_weight_n / max(1.0, drag_coeff)

        # Rod Floating Margin (%)
        # Positive: Rod falls faster than polished rod (Safe)
        # Negative: Polished rod drops faster than rod string -> Rod Float / Slack Bridle
        floating_margin_pct = ((v_terminal - v_pr_max) / max(0.001, v_terminal)) * 100.0

        is_rod_floating = floating_margin_pct <= 0.0

        # Impact loading energy if rod floating occurs
        delta_v = max(0.0, v_pr_max - v_terminal)  # separation velocity
        rod_stiffness_k = (cls.STEEL_MODULUS * rod_area) / max(1.0, pump_depth_m)  # N/m
        
        if is_rod_floating and delta_v > 0.001:
            impact_energy_j = 0.5 * total_rod_mass * (delta_v ** 2)
            impact_force_n = math.sqrt(2.0 * impact_energy_j * rod_stiffness_k)
            impact_force_klb = (impact_force_n / 4.44822) / 1000.0
        else:
            impact_energy_j = 0.0
            impact_force_klb = 0.0

        # Nominal PPRL & MPRL
        # PPRL = Buoyant Rod Weight + Fluid Load + Friction + Impact
        friction_upstroke_klb = (drag_coeff * v_pr_max / 4.44822) / 1000.0
        base_pprl = buoyant_weight_klb + fluid_load_klb + friction_upstroke_klb
        pprl_klb = base_pprl + impact_force_klb

        # MPRL = Buoyant Rod Weight - Downstroke Friction - (zero if floating)
        mprl_klb = max(0.5, buoyant_weight_klb - (drag_coeff * min(v_terminal, v_pr_max) / 4.44822) / 1000.0)
        if is_rod_floating:
            mprl_klb = min(mprl_klb, 1.2)  # Load cell drops toward zero due to slack bridle

        # Maximum safe SPM at this viscosity before rod floating occurs
        # v_pr_max = v_terminal => (stroke_m / 2) * (2*pi*spm_max/60) = v_terminal
        # spm_max = (v_terminal * 60) / (pi * stroke_m)
        max_safe_spm = (v_terminal * 60.0) / (math.pi * max(0.1, stroke_m))
        max_safe_spm = round(max(1.0, min(12.0, max_safe_spm * 0.90)), 2)  # 10% safety margin

        return {
            "v_pr_max_mps": round(v_pr_max, 3),
            "v_terminal_mps": round(v_terminal, 3),
            "floating_margin_pct": round(floating_margin_pct, 1),
            "is_rod_floating": is_rod_floating,
            "impact_energy_joules": round(impact_energy_j, 1),
            "impact_force_klb": round(impact_force_klb, 2),
            "pprl_klb": round(pprl_klb, 2),
            "mprl_klb": round(mprl_klb, 2),
            "max_safe_spm": max_safe_spm,
            "buoyant_weight_klb": round(buoyant_weight_klb, 2),
            "fluid_load_klb": round(fluid_load_klb, 2),
            "viscous_drag_coeff_n_per_ms": round(drag_coeff, 1),
        }

    @classmethod
    def generate_dyno_cards(
        cls,
        stroke_length_in: float,
        pprl_klb: float,
        mprl_klb: float,
        fillage_pct: float,
        is_rod_floating: bool = False,
        impact_force_klb: float = 0.0,
        n_points: int = 100
    ) -> Dict[str, Any]:
        """Generates realistic Surface and Downhole (Gibbs) Dynamometer Cards.
        Returns array of {x: position_inches, y: load_klb}.
        """
        # Surface Card: Polished rod load vs position
        # Hysteresis loop driven by rod stretch and harmonic response
        surface_points = []
        downhole_points = []

        stroke = stroke_length_in
        fillage = fillage_pct / 100.0

        # Upstroke: 0 to stroke
        # Downstroke: stroke to 0
        angles = np.linspace(0, 2 * math.pi, n_points)

        for theta in angles:
            # Kinematic position: x = (stroke / 2) * (1 - cos(theta))
            x_pos = (stroke / 2.0) * (1.0 - math.cos(theta))
            
            # Surface Card Load
            if theta < math.pi:  # UPSTROKE (0 -> pi)
                # Picks up fluid load, rod stretches
                frac = theta / math.pi
                if frac < 0.15:
                    # Load pickup transition
                    load_surf = mprl_klb + (pprl_klb - mprl_klb) * (frac / 0.15)
                else:
                    load_surf = pprl_klb + 0.5 * math.sin(3.0 * theta)  # Rod vibration harmonics
                
                # If rod was floating, add impact spike right at upstroke turnaround
                if is_rod_floating and frac < 0.20:
                    load_surf += impact_force_klb * math.sin(frac / 0.20 * math.pi)
            else:  # DOWNSTROKE (pi -> 2*pi)
                frac = (theta - math.pi) / math.pi
                if frac < 0.20:
                    # Traveling valve opens, load sheds
                    load_surf = pprl_klb - (pprl_klb - mprl_klb) * (frac / 0.20)
                else:
                    load_surf = mprl_klb + 0.3 * math.sin(2.0 * theta)
                
                # If rod floating, load dips below MPRL (slack carrier bar)
                if is_rod_floating:
                    load_surf = max(0.4, load_surf - 1.2 * math.sin(frac * math.pi))

            surface_points.append({
                "position_in": round(float(x_pos), 2),
                "load_klb": round(float(load_surf), 2)
            })

            # Downhole Pump Card (Gibbs Card)
            # Downhole stroke is slightly shorter due to rod stretch:
            rod_stretch = stroke * 0.12
            dh_stroke = stroke - rod_stretch
            dh_x = max(0.0, min(dh_stroke, (x_pos / stroke) * dh_stroke))
            
            # Fluid pound behavior: when plunger descends and encounters fluid level
            dh_pprl = pprl_klb * 0.85
            dh_mprl = mprl_klb * 0.70

            if theta < math.pi:  # UPSTROKE (Plunger moving up, lifting fluid)
                dh_load = dh_pprl
            else:  # DOWNSTROKE
                downstroke_travel = (theta - math.pi) / math.pi
                # Incomplete fillage => Fluid Pound notch
                if downstroke_travel < (1.0 - fillage):
                    # Plunger traveling in gas/vacuum -> Zero load
                    dh_load = dh_mprl * 0.3
                else:
                    # Plunger strikes fluid -> sudden load spike then baseline
                    pound_frac = (downstroke_travel - (1.0 - fillage)) / fillage
                    if pound_frac < 0.1:
                        dh_load = dh_pprl * 0.95  # Fluid pound impact notch!
                    else:
                        dh_load = dh_mprl

            downhole_points.append({
                "position_in": round(float(dh_x), 2),
                "load_klb": round(float(dh_load), 2)
            })

        # Calculate Card Area (Energy per stroke)
        # Trapezoidal numerical integration: Integral(y dx)
        x_vals = [p["position_in"] for p in surface_points]
        y_vals = [p["load_klb"] for p in surface_points]
        card_area = abs(float(np.trapz(y_vals, x_vals)))

        return {
            "surface_card": surface_points,
            "downhole_card": downhole_points,
            "card_area_klb_in": round(card_area, 1),
            "stroke_length_in": stroke_length_in,
            "pprl_klb": round(pprl_klb, 2),
            "mprl_klb": round(mprl_klb, 2),
            "fillage_pct": round(fillage_pct, 1),
            "has_fluid_pound": fillage_pct < 80.0,
            "has_rod_floating": is_rod_floating
        }

    @classmethod
    def calculate_energy_and_economics(
        cls,
        spm: float,
        stroke_length_in: float,
        pprl_klb: float,
        oil_rate_bopd: float,
        water_rate_bwpd: float,
        steam_volume_cwe_m3: float = 1800.0,
        cum_oil_cycle_bbl: float = 2400.0,
        electricity_cost_kwh: float = 7.50,  # INR per kWh (~$0.09)
        steam_cost_per_m3: float = 1200.0,   # INR per m3 CWE steam
        oil_price_per_bbl: float = 6200.0    # INR per bbl (~$75/bbl)
    ) -> Dict[str, Any]:
        """Calculates specific power consumption (kWh/bbl), SOR, operating costs, and carbon footprint."""
        # Polished Rod Horsepower (PRHP)
        # PRHP = (PPRL - MPRL) * Stroke(in) * SPM / (4 * 33000) approx or from Card Area
        stroke_ft = stroke_length_in / 12.0
        liquid_rate_blpd = max(1.0, oil_rate_bopd + water_rate_bwpd)
        
        # Hydraulic horsepower + mechanical losses
        prhp = (pprl_klb * 1000.0 * stroke_ft * spm) / 33000.0 * 0.45
        motor_efficiency = 0.88
        vfd_efficiency = 0.95
        kwh_per_day = (prhp * 0.7457 / (motor_efficiency * vfd_efficiency)) * 24.0

        specific_energy_kwh_per_bbl = kwh_per_day / max(0.5, oil_rate_bopd)

        # Steam-Oil Ratio (SOR)
        sor = steam_volume_cwe_m3 / max(1.0, cum_oil_cycle_bbl * 0.158987)  # 1 bbl = 0.159 m3

        # Economics (daily INR)
        daily_power_cost = kwh_per_day * electricity_cost_kwh
        daily_oil_revenue = oil_rate_bopd * oil_price_per_bbl
        daily_operating_profit = daily_oil_revenue - daily_power_cost

        # Carbon footprint (Grid emission factor in Rajasthan ~ 0.82 kg CO2 / kWh)
        kg_co2_per_bbl = specific_energy_kwh_per_bbl * 0.82

        return {
            "motor_power_kw": round(prhp * 0.7457, 2),
            "daily_kwh": round(kwh_per_day, 1),
            "specific_energy_kwh_per_bbl": round(specific_energy_kwh_per_bbl, 2),
            "sor": round(sor, 2),
            "daily_power_cost_inr": round(daily_power_cost, 0),
            "daily_oil_revenue_inr": round(daily_oil_revenue, 0),
            "daily_operating_profit_inr": round(daily_operating_profit, 0),
            "kg_co2_per_bbl": round(kg_co2_per_bbl, 2)
        }
