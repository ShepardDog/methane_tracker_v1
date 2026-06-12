 # -------------------------
# Methane emissions baseline (Global Methane Budget 2023, Saunois et al.)
# Values in Mt CH4 per year
# -------------------------

import math
import numpy as np
import pandas as pd
from dataclasses import dataclass


rates = {
    #s is the sensitivity coefficient for CH₄ oxidation. 
    "s": 0.3,
    "ppb_ch4": 1922,
    #Needs source checking
    "mt_to_ppb_co2": 0.128,  # Conversion factor from Mt CO₂ to ppm in the atmosphere (approximate)
    "mt_to_ppb_ch4": 0.35,  # Conversion factor from Mt CH₄ to ppb in the atmosphere (approximate)
    "ch4_to_co2_mass": 44/16 # Molecular weight ratio (44/16)
}

base_line = {
    "ch4": 5480,
    "co2": 41000, 
    "ch4_ppb": 1922,
    "co2_ppb": 410000
}

offsets = {
    "ch4_p": 0,
    "co2_p": 0,
    "temp_p": 0,
    "ice_p": 0
}
new_emissions = {
    "ch4": 0,
    "co2": 0.0
}



fossil_fuel = pd.DataFrame([
    {"fuel": "coal", "phase": 1, "years": 10, "rate": -0.005},
    {"fuel": "coal", "phase": 2, "years": 5,  "rate": -0.01},
    {"fuel": "coal", "phase": 3, "years": 5,  "rate": -0.01},
    {"fuel": "oil",  "phase": 1, "years": 10, "rate": 0.03},
    {"fuel": "oil",  "phase": 2, "years": 5,  "rate": 0.0},
    {"fuel": "oil",  "phase": 3, "years": 5,  "rate": -0.005},
    {"fuel": "gas",  "phase": 1, "years": 10, "rate": 0.015},
    {"fuel": "gas",  "phase": 2, "years": 5,  "rate": 0.005},
    {"fuel": "gas",  "phase": 3, "years": 5,  "rate": 0.0},
])




growth_rates = {
    "animal_ag": {"rate": 0.17, "years": 9},
    "landfills": {"rate": 0.5, "years": 25},
    "paddy": {"rate": 0.044, "years": 9},
}

ch4_emission = {
    "animal_ag": 120,   # livestock enteric + manure
    "paddy": 40,
    "landfills": 65,       # landfills + wastewater
    "coal": 40,    
    "oil": 45,
    "gas": 35,     
    "wetlands": 180,
    "unit" : "Mt CH₄/year"   
    # "biomass_burning": 35     # for now optional, could add later
}

sector_list = ["animal_ag", "paddy", "landfills"] 
fossil_fuel_list = ["coal", "oil", "gas"]

@dataclass(frozen=True) 
class ch4parameters:
    ref_stock: float = 5480.0
    ref_tau: float = 11.8  # Reference lifetime of methane in years (approximate)
    sensitivity_coefficient: float = 0.3  
    ppb_ch4:float = 1922 
    
#2024 NOAA global Monitoring Laboratory, Earth System Research Laboratory, Global Greenhouse Gas Reference Network.
#ref_CH4_PPB=1926.56 * 2.84 ~ 5480 Tg


@dataclass(frozen=True)
class RadiativeForcing:
    CH4_PPB_M0: float = 720.0  # Pre-industrial methane concentration in ppb
    RF_CONSTANT: float = 0.036  # Radiative efficiency constant for methane (W/m² per ppb), based on Myhre et al. and updated by IPCC assessment reports.
    N2O_REF_PPB: float = 270 # Reference ppb of N20) (approximate value in 1850)
    CH4_N2O_OVERLAP_SCALE = 0.47
    H2O_FEEDBACK_SCALE: float = 1.15
    
     
