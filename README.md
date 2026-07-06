🧊 PoleWatch: Arctic Methane Logic (V1.0)A System Dynamics Framework for Sectoral Emissions & Arctic Restoration Overview. MVP - Minimal Viable Physics

PoleWatch is an independent research tool designed to visualize the impact of specific methane (CH₄) sources on the Arctic energy balance. 
Core Features (V.0.5)
First-Order Decay Engine: Implements a linear oxidation model (8.3% annual decay) to track atmospheric stock over a 20-year horizon.
Sectoral Isolation: Independent variables for enteric fermentation, rice cultivation, and fossil fuel leakages.Arctic Restoration Modules: Quantifiable offsets based on Peatland restoration and Kelp/Tundra sequestration rates.Black Carbon (Soot) Logic: Integration of albedo-loss metrics driven by shipping and flaring.

⚠️ Known Limitations 
(V1.0) This version serves as a functional baseline and utilizes the following simplifications

Linear Oxidation Constant: 

V1.0 assumes a fixed 8.3% oxidation rate. It does not yet account for the non-linear "step-response" or the chemical competition for OH radicals in the atmosphere. 
Static Baseline: 
The model utilizes the Global Methane Budget 2023 as a fixed starting point. It does not currently account for dynamic "Natural Feedback" increases (e.g., accelerating permafrost thaw).

Simplified Radiative Forcing: 
The conversion from mass (Mt) to temperature (Delta T) uses a standardized coefficient that does not account for spectral overlap with other greenhouse gases.

Albedo Feedback: 
While Black Carbon is tracked, the self-reinforcing loop of sea-ice loss (Albedo Feedback) is modeled as a linear impact rather than an exponential acceleration.

🚀 Roadmap (V1.5 & V2.0)
V1.5: "The Physics Upgrade" GWP Methodology:

Transition from GWP100 to GWP to better reflect the short-lived nature of methane as a "flow" gas.
Non-Linear Decay: Implementation of a variable oxidation curve based on atmospheric chemistry projections.
UI Overhaul: Migration from "Ugly UI" to an Arctic-themed Glassmorphism dashboard with interactive gauge charts.
V2.0: "The Biological Bridge" Species Survival Metrics: Linking temperature deltas directly to sea-ice thickness and habitat loss for polar bears and seals.
Dynamic Permafrost Integration: Adding a "Tipping Point" toggle to simulate methane release from thawing tundra.

Technical Stack Language: 
Python 3.x
Framework: StreamlitData 
Sources: Global Methane Budget (Saunois et al.), NOAA, IPCC AR6.
