# Data Dictionary & Tag Specifications
## Baghewala Heavy Oil Asset (SIH 26120)

| Tag ID | Parameter Name | Physical Unit | Expected Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `Reservoir_Wellbore_Temp_C` | Wellbore Temperature | °C | 46.0 – 195.0 | Post-steam in-situ fluid temperature |
| `Oil_Viscosity_cP` | Crude Oil Viscosity | cP | 25.0 – 50,000.0 | Viscosity derived from Andrade-Walther law |
| `Oil_Rate_bopd` | Oil Flow Rate | bopd | 0.0 – 150.0 | Daily produced net oil volume |
| `Water_Rate_bwpd` | Water Flow Rate | bwpd | 0.0 – 250.0 | Daily produced formation & condensed steam water |
| `Watercut_pct` | Watercut | % | 0.0 – 98.0 | Volumetric fraction of water in total liquid |
| `Bottomhole_Pressure_kPa` | Bottomhole Pressure (BHP) | kPa | 1,500 – 5,500 | In-situ reservoir flow pressure |
| `SPM` | Pumping Speed | SPM | 2.0 – 10.5 | Strokes Per Minute of surface walking beam |
| `VFD_Frequency_Hz` | Surface VFD Frequency | Hz | 25.0 – 65.0 | Variable Frequency Drive output frequency |
| `Stroke_Length_in` | Polished Rod Stroke | inches | 86.0 – 144.0 | Total travel of horsehead per cycle |
| `Pump_Fillage_pct` | Pump Barrel Fillage | % | 40.0 – 100.0 | Ratio of fluid volume entering pump barrel |
| `PPRL_klb` | Peak Polished Rod Load | klb | 5.0 – 22.0 | Maximum upward rod tensile load |
| `MPRL_klb` | Minimum Polished Rod Load | klb | 0.5 – 12.0 | Minimum downward load on carrier bar |
| `Rod_Floating_Margin_pct` | Floating Margin | % | -50.0 – 100.0 | Relative velocity margin between rod sinking & PR downward speed |
| `Prob_Failure_7d` | 7-Day Failure Risk | Probability | 0.00 – 1.00 | Likelihood of mechanical failure within 7 operational days |
