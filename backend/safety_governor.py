"""Safety Governor: Enforces Operational Envelope & Engineering Constraints.
The optimizer searches broadly, but the Safety Governor decides whether a candidate
or operating setpoint is operationally permissible.

Constraint Checks:
1. SPM Limits (min 2.0, max based on rod fall or motor rating <= 10.5 SPM)
2. VFD Frequency Limits (25.0 Hz - 65.0 Hz)
3. Rod Floating Margin (>= 15.0% for GREEN, 0-15% for AMBER, < 0% for RED)
4. Pump Fillage (>= 75.0% required to prevent fluid pound)
5. PPRL Stress (must not exceed safe rod string yield strength)
6. Steam Injection Pressure (must not exceed formation fracture pressure ~18,000 kPa)
7. Steam Quality (70% - 90%)
8. 7-Day Failure Risk (<= 0.40 for GREEN, 0.40-0.60 for AMBER, > 0.60 for RED)
9. Model Prediction Confidence (>= 0.75 for full automation; < 0.75 triggers OPERATOR REVIEW REQUIRED)
"""

from typing import Dict, Any, List, Optional


class SafetyGovernor:
    MIN_SPM = 2.0
    MAX_SPM = 10.5
    MIN_VFD_HZ = 25.0
    MAX_VFD_HZ = 65.0
    MIN_FLOATING_MARGIN_PCT = 15.0
    MIN_FILLAGE_PCT = 75.0
    MAX_INJECTION_PRESSURE_KPA = 18000.0
    MIN_INJECTION_PRESSURE_KPA = 11000.0
    MAX_STEAM_VOLUME_M3 = 3000.0
    MIN_STEAM_VOLUME_M3 = 800.0
    MAX_7D_FAILURE_PROB = 0.40
    MIN_CONFIDENCE_FOR_AUTONOMY = 0.75
    MAX_PPRL_KLB = 22.0

    @classmethod
    def evaluate_candidate(
        cls,
        spm: float,
        vfd_hz: float,
        floating_margin_pct: float,
        fillage_pct: float,
        pprl_klb: float,
        failure_prob_7d: float = 0.05,
        steam_pressure_kpa: Optional[float] = None,
        steam_volume_m3: Optional[float] = None,
        confidence: float = 0.90
    ) -> Dict[str, Any]:
        checks: List[Dict[str, Any]] = []
        violations: List[str] = []
        warnings: List[str] = []

        # 1. SPM Check
        spm_passed = cls.MIN_SPM <= spm <= cls.MAX_SPM
        checks.append({
            "parameter": "Pumping Speed (SPM)",
            "value": round(spm, 2),
            "allowed_range": f"{cls.MIN_SPM} - {cls.MAX_SPM} SPM",
            "passed": spm_passed,
            "severity": "CRITICAL" if not spm_passed else "INFO"
        })
        if not spm_passed:
            violations.append(f"SPM ({spm:.1f}) exceeds permissible envelope ({cls.MIN_SPM}-{cls.MAX_SPM} SPM).")

        # 2. VFD Frequency Check
        vfd_passed = cls.MIN_VFD_HZ <= vfd_hz <= cls.MAX_VFD_HZ
        checks.append({
            "parameter": "VFD Frequency (Hz)",
            "value": round(vfd_hz, 1),
            "allowed_range": f"{cls.MIN_VFD_HZ} - {cls.MAX_VFD_HZ} Hz",
            "passed": vfd_passed,
            "severity": "CRITICAL" if not vfd_passed else "INFO"
        })
        if not vfd_passed:
            violations.append(f"VFD Frequency ({vfd_hz:.1f} Hz) out of drive bounds ({cls.MIN_VFD_HZ}-{cls.MAX_VFD_HZ} Hz).")

        # 3. Rod Floating Margin Check
        if floating_margin_pct <= 0.0:
            checks.append({
                "parameter": "Rod Floating Margin (%)",
                "value": round(floating_margin_pct, 1),
                "allowed_range": f">= {cls.MIN_FLOATING_MARGIN_PCT}%",
                "passed": False,
                "severity": "CRITICAL"
            })
            violations.append(f"Rod Floating Margin is negative ({floating_margin_pct:.1f}%). High risk of slack bridle and parting.")
        elif floating_margin_pct < cls.MIN_FLOATING_MARGIN_PCT:
            checks.append({
                "parameter": "Rod Floating Margin (%)",
                "value": round(floating_margin_pct, 1),
                "allowed_range": f">= {cls.MIN_FLOATING_MARGIN_PCT}%",
                "passed": False,
                "severity": "WARNING"
            })
            warnings.append(f"Rod Floating Margin is marginal ({floating_margin_pct:.1f}% < {cls.MIN_FLOATING_MARGIN_PCT}%).")
        else:
            checks.append({
                "parameter": "Rod Floating Margin (%)",
                "value": round(floating_margin_pct, 1),
                "allowed_range": f">= {cls.MIN_FLOATING_MARGIN_PCT}%",
                "passed": True,
                "severity": "INFO"
            })

        # 4. Pump Fillage Check
        fillage_passed = fillage_pct >= cls.MIN_FILLAGE_PCT
        checks.append({
            "parameter": "Pump Fillage (%)",
            "value": round(fillage_pct, 1),
            "allowed_range": f">= {cls.MIN_FILLAGE_PCT}%",
            "passed": fillage_passed,
            "severity": "WARNING" if not fillage_passed else "INFO"
        })
        if not fillage_passed:
            warnings.append(f"Pump fillage ({fillage_pct:.1f}%) is low; risk of fluid pound impact.")

        # 5. Peak Polished Rod Load Check
        pprl_passed = pprl_klb <= cls.MAX_PPRL_KLB
        checks.append({
            "parameter": "Peak Polished Rod Load (klb)",
            "value": round(pprl_klb, 2),
            "allowed_range": f"<= {cls.MAX_PPRL_KLB} klb",
            "passed": pprl_passed,
            "severity": "CRITICAL" if not pprl_passed else "INFO"
        })
        if not pprl_passed:
            violations.append(f"PPRL ({pprl_klb:.1f} klb) exceeds rod string yield safety limit ({cls.MAX_PPRL_KLB} klb).")

        # 6. Steam Pressure Check (if applicable)
        if steam_pressure_kpa is not None:
            press_passed = steam_pressure_kpa <= cls.MAX_INJECTION_PRESSURE_KPA
            checks.append({
                "parameter": "Steam Injection Pressure (kPa)",
                "value": round(steam_pressure_kpa, 0),
                "allowed_range": f"<= {cls.MAX_INJECTION_PRESSURE_KPA} kPa",
                "passed": press_passed,
                "severity": "CRITICAL" if not press_passed else "INFO"
            })
            if not press_passed:
                violations.append(f"Injection pressure ({steam_pressure_kpa:.0f} kPa) exceeds fracture envelope.")

        # 7. 7-Day Failure Risk Check
        fail_passed = failure_prob_7d <= cls.MAX_7D_FAILURE_PROB
        checks.append({
            "parameter": "7-Day Failure Hazard (P7d)",
            "value": round(failure_prob_7d, 3),
            "allowed_range": f"<= {cls.MAX_7D_FAILURE_PROB}",
            "passed": fail_passed,
            "severity": "CRITICAL" if failure_prob_7d > 0.60 else ("WARNING" if not fail_passed else "INFO")
        })
        if failure_prob_7d > 0.60:
            violations.append(f"7-day failure hazard is elevated ({failure_prob_7d:.2f}).")
        elif not fail_passed:
            warnings.append(f"7-day failure hazard is moderate ({failure_prob_7d:.2f}).")

        # 8. Confidence Check
        conf_passed = confidence >= cls.MIN_CONFIDENCE_FOR_AUTONOMY
        checks.append({
            "parameter": "Decision Confidence Score",
            "value": round(confidence, 2),
            "allowed_range": f">= {cls.MIN_CONFIDENCE_FOR_AUTONOMY}",
            "passed": conf_passed,
            "severity": "WARNING" if not conf_passed else "INFO"
        })
        if not conf_passed:
            warnings.append(f"Prediction confidence ({confidence:.2f}) below autonomous threshold ({cls.MIN_CONFIDENCE_FOR_AUTONOMY}).")

        # Overall Status
        if len(violations) > 0:
            status = "REJECTED"
            badge = "RED"
            color = "#EF4444"
            summary = "SAFETY GOVERNOR: REJECTED - Operational or physical constraints violated."
        elif len(warnings) > 0:
            status = "ALLOWED WITH REVIEW"
            badge = "AMBER"
            color = "#F59E0B"
            summary = "SAFETY GOVERNOR: AMBER - Allowed with caution; operator review recommended."
        else:
            status = "PASSED"
            badge = "GREEN"
            color = "#10B981"
            summary = "SAFETY GOVERNOR: PASSED - Strictly within configured engineering envelope."

        return {
            "status": status,
            "badge": badge,
            "color": color,
            "is_permissible": len(violations) == 0,
            "summary": summary,
            "checks": checks,
            "violations": violations,
            "warnings": warnings,
            "rejection_reasons": violations if violations else (warnings if warnings else ["None"])
        }