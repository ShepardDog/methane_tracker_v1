🧊 PoleWatch: Methane to Melt (M2M)- A Reduced-Order Methane Climate Mode (V0.5)
🌍 Methane Engine — README 
1. Overview - Version 0.5 - Minimal Viable Physics MVP
M2 M is an independent research tool designed to visualize the impact of specific methane (CH₄) sources on the Arctic energy balance.
The methane engine simulates atmospheric CH₄ concentration, radiative forcing, and warming over a user‑defined time horizon (up to 20 in the app). It uses:

Yearly timesteps
End‑of‑year state updates
Physically grounded oxidation
Sector‑specific emissions
Etminan et al. (2016) radiative forcing
IPCC AR6 climate sensitivity
The engine outputs:
CH₄ stock (Tg)
CH₄ concentration (ppb)
Radiative forcing (W/m²)
Warming (°C)
Δforcing and Δwarming relative to “current” conditions

2. Model Assumptions
Time evolves in yearly steps.
Within each year:
Oxidation acts on the existing CH₄ stock.
New emissions are added.
Oxidation follows a constant fractional decay based on lifetime.
Emissions from each sector are modeled independently.
Wetland emissions are constant in v0.5 (temperature‑dependent in v1).
Radiative forcing uses the Etminan non‑linear formula.
Climate sensitivity uses IPCC AR6 λ = 0.8 °C per W/m².

Emissions Model
Anthropogenic sectors
Animal agriculture
Paddy cultivation
Landfills & wastewater
Each has a BAU growth rate and a slider‑adjusted growth rate

Animal Ag has a Humane phaseout curve- this assumes that it will take over unrealistic input such as cut down animal ag emissions by 100% in one year- this is not possible as animals have a natural life span and in this model, we respect the lives of the individuals 

Fossil fuels
Three‑phase model:
Phase 1 (10 years)
Phase 2 (5 years)
Phase 3 (5 years)
Each phase has its own growth rate.

Natural emissions
Wetlands = constant 180 Mt/year (v0.5) 


Known Limitations of V0.5

Wetlands are constant (no temperature feedback yet).
No CO₂ engine yet (methane‑only warming looks small).
No CH₄–OH feedback loop beyond lifetime scaling.
Arctic amplification kept simple with a factor of ).


Road Map
M2 M will have versions v0.5 through v2.0

V0.6
Arctic Restoration Modules: 
Peatland restoration and Kelp/Tundra sequestration rates.
Black Carbon (Soot) Logic: 
Integration of albedo-loss metrics driven by shipping and flaring.
Create data files from each run
Add visualizations 




Technical Stack Language used so far : 
Python 3.x
Numpy and Python Pandas
Framework: StreamlitData 

Sources: Global Methane Budget (Saunois et al.), NOAA, IPCC AR6.
