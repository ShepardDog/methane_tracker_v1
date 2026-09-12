# -------------------------
# Methane emissions baseline (Global Methane Budget 2023, Saunois et al.)
# Values in Mg CH4 per year
# -------------------------
# Param default rule: if a value could plausibly vary per call/scenario (site params, 
# things with a literature range), give it an argument-level default. If it's a fixed 
# physical/mathematical constant that should never change per call, keep it out of the 
# signature entirely and reference the module-level constant in the function body.

import numpy as np
import pandas as pd
from dataclasses import dataclass, field


#source cards

@dataclass(frozen=True) 
class ch4parameters:
    ref_stock: float = 5480
    ref_stock_unit: str = "Tg CH4"
    ref_tau: float = 11.8  # Reference lifetime of methane in years (approximate)
    sensitivity_coefficient: float = 0.3  
    ppb_ch4:float = 1933

ch4_params = ch4parameters()

@dataclass(frozen=True)
class co2parameters:
    ref_stock:float = 3.38e6 
    ppm_co2:float = 424
    ch4_to_co2_mass:float = 44/16
    CO2_ppm:np.ndarray = field(
        default_factory=lambda: np.array([425, 426, 428, 429, 430, 431, 432, 433, 434, 435, 435, 436, 436, 437, 437, 437, 437, 437, 437, 437, 438 ])) #SPP1 , with projected 1.5 ℃
    CO2_ppm_baseline:float = 280
    coefficient: float= 5.35 #radiative_forcing_coefficient for CO2
    atmospheric_conversion_factor: float = 2130 # CO₂ Information Analysis Center. multiplying by this factor will convert to ppm (2130Tg carbon is considered equivalant to 1PPM )
co2_params = co2parameters()

ch4_baseline = ch4_params.ref_stock
co2_baseline = co2_params.ref_stock
arctic_factor = 3.0  # Amplification factor for Arctic temperature relative to global temperature

carbon_sinks= {
    "tundra":{"label":"","min_value": 0, "max_value": 500_000, "value": 0, "emoji":"🌱",  "step":100, "key":"tundra", "format":"%d%%", "help":"Area of tundra restored. Impacts CH₄ emissions and surface albedo.", "title":"Tundra Restoration (Ha)"},
    "kelp_cultivation":{"label":"kelp","min_value": 0, "max_value":1_000_000, "value":0, "emoji":"🌿" ,"step":100, "key":"kelp", "format":"%d%%", "help":"", "title":"Kelp Cultivation (ha)"}, 
    "peatland_restoration":{"label":"peat","min_value": 0, "max_value": 800_000, "value":0, "emoji":"🌾" ,"step":150, "key":"peat", "format":"%d%%", "help":"", "title":"Peatland restoration (ha)"}, 
    
    }

bio_engineered_sinks ={
     "methnotrophic_tropics":{"label": "mtrophic_tropical", "min_value": 0, "max_value":600_000, "value": 0, "emoji":"🧫", "step": 100_000, "key":"tropic_methanotropic", "help":"Targeted deployment of methane-eating bacteria (methanotrophs) into wild wetlands.", "title":"Methanotrophic Tropical Wet Lands" },
     "methnotrophic_arctic":{"label": "mtrophic_arctic", "min_value": 0, "max_value":150_000, "value": 0, "emoji":"🦠", "step": 25_000, "key":"arctic_methanotropic", "help":"Targeted deployment of methane-eating bacteria (methanotrophs) into wild wetlands.", "title":"Methanotrophic Arctic Wetlands" }

}

geo_engineered_sinks ={
    "sea_ice_cover":{"label":"sea_ice","min_value": 0, "max_value": 4_500_000, "value":0, "emoji":"❄️" ,"step":850, "key":"sea_ice","format":"%d%%", "help":"","title":"Sea Ice Cover (Km²)."}, 
    "cloud_brightening":{"label":"cloud","min_value": 0, "max_value": 100, "value":0, "emoji":"🌨️" ,"step":10, "key":"cloud", "format":"%d%%", "help":"", "title":"Cloud Brightening"}   
}

emitters = {
    "animal_ag":{"label":"Animal Agriculture","min_value":-100, "max_value": 0, "value":0, "emoji":"🐄" ,"step":5, "key":"animal_ag", "format":"%d%%", "help":"", "title":"Animal Agriculture"},  
    "paddy":{"label":"Paddy","min_value":-40, "max_value": 0, "value":0, "emoji":"🍚" ,"step":5, "key":"paddy", "format":"%d%%", "help":"", "title":"Paddy Cultivation"}, 
    "landfills":{"label":"Land Fills","min_value":-100, "max_value": 0, "value": 0, "emoji":"🚮" ,"step":5, "key":"landfills", "format":"%d%%", "help":"", "title":"Landfills"}, 
    }

emitters_fossil={

    "coal":{"label":"Coal","min_value":-100, "max_value": 0, "value":0, "emoji":"🪨☁" ,"step":5, "key":"coal", "format":"%d%%", "help":"", "title":"Coal"}, 
    "oil":{"label":"Petrolium Oil","min_value":-100, "max_value": 0, "value":0, "emoji":"⛽" ,"step":5, "key":"oil", "format":"%d%%", "help":"", "title":"Petrolium Oil"}, 
    "gas":{"label":"Natural Gas","min_value":-100, "max_value": 0, "value":0, "emoji":"♨️" ,"step":5, "key":"gas", "format":"%d%%", "help":"", "title":"Natural Gas"}, 

}


black_carbon ={
    "shipping":{"label":"Shipping","min_value":-100, "max_value": 0, "value":0, "emoji":"🚢" ,"step":5, "key":"shipping", "format":"%d%%", "help":"", "title":"Shipping"}, 
    "flares":{"label":"Flares","min_value":-100, "max_value": 0, "value":0, "emoji":"🔥 🏭" ,"step":5, "key":"flares", "format":"%d%%", "help":"", "title":"Flares"}, 
    "transport":{"label":"Transport","min_value":-100, "max_value": 0, "value":0, "emoji":"🚗💨" ,"step":5, "key":"transport", "format":"%d%%", "help":"", "title":"Land Transport"}
}

#These emissions can not direclty controlled by humans - there for the UI will not give out a value
natural_emissions ={
    "wetlands":{"label":"Wetlands","min_value":-100, "max_value": 0, "value":0, "emoji":"🦆" ,"step":100, "key":"wetlands", "format":"%d%%", "help":"Natural methane (CH₄) emissions from wetlands. While not directly controllable, they generally decrease as climate warming is reduced. Wetlands also provide important ecological and climate benefits.", "title":"Wetlands"}

}



card_baseline_ch4 ={
    
    "ch4_baseline" :{"variable":ch4_baseline,"unit":"Tg", "description":"Current Atmospheric CH₄"}
}

card_baseline_co2 ={
    "co2_baseline" :{"variable":co2_baseline, "unit":"Tg", "description":"Current Atmospheric CO₂"}
}

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

#IEA Global Methane Tracker 2026
ch4_emission = {
    "animal_ag": 120,   # livestock enteric + manure
    "paddy": 40,
    "landfills": 65,       # landfills + wastewater
    "coal": 43,    
    "oil": 45,
    "gas": 35,     
    "wetlands": 180,
    "unit" : "Tg CH₄/year"   
    # "biomass_burning": 35     # for now optional, could add later
}

sector_list = ["animal_ag", "paddy", "landfills"] 
fossil_fuel_list = ["coal", "oil", "gas"]

 
    
#2024 NOAA global Monitoring Laboratory, Earth System Research Laboratory, Global Greenhouse Gas Reference Network.
#ref_CH4_PPB=1926.56 * 2.84 ~ 5480 Tg


@dataclass(frozen=True)
class radiative_forcing:
    CH4_PPB_M0: float = 722.0  # Pre-industrial methane concentration in ppb
    RF_CONSTANT: float = 0.036  # Radiative efficiency constant for methane (W/m² per ppb), based on Myhre et al. and updated by IPCC assessment reports.
    N2O_REF_PPB: float = 270 # Reference ppb of N20) (approximate value in 1850)
    lambda_sensitivity: float = 0.8  # Climate sensitivity parameter (W/m² per °C)

radiative = radiative_forcing()

#Arctic storm probabilities
storm_prob = {1:0.6, 2:0.55, 3:0.5, 4:0.4, 5: 0.3, 6:0.2, 7: 0.2, 8:0.25, 9:0.4, 10:0.55, 11:0.6,12:0.65 }

# TODO: V0.6+ 
# value taken from  Sacchrina latissima
# Assumed constant in V0.5
# Seasonal variability ignored
# See Smith et al. 2023

@dataclass(frozen=True)
class biomass_growth:
    max_density_per_ha: float = 0.00003  # Carrying capacity for kelp # between 30 to 40 per ha in Tg/ha (based on literature values)
    initial_weight: float = 5e-9  # Initial biomass - starter seed weight in Tg/ha (based on literature values)
    dry_weight_fraction: float = 0.1   # Fraction of kelp biomass that is dry weight (based on literature values)
    carbon_fraction : float = 0.32  # Fraction of dry weight that is carbon (based on literature values) between 0.3 to 0.35
    CO2_weight : float = 44/12 # Conversion factor from carbon to CO2 (based on molecular weights)
    kelp_growth_rates = np.array([0.0, 0.4, 0.7, 0.8, 0.5, 0.5, 0.6, 0.5, 0.3, 0.2, 0.1, 0.0]) #place holder values for the kelp growths Feb - Jan 

KELP_PARAMETERS = biomass_growth()


@dataclass(frozen=True)
#new: float = (1- 0.45) means the damage caused by level 1 strom for young kelp growth is 45% of the growth will be wipped off. 1 - 0.45= 0.55 of the mass will remain 
class storm_impact1:
    
    new: float =(1 -0.45) # young kelp growth > 1 year
    medium: float =(1- 0.35) # kelp growth bet 1 to 2 years 
    mature: float =(1 - 0.25) # kelp growth > 2 years
IMPACT1 = storm_impact1()

class storm_impact2:
    
    new: float = (1- 0.55) # young kelp growth > 1 year
    medium: float =(1- 0.45) # kelp growth bet 1 to 2 years 
    mature: float =(1- 0.35) # kelp growth > 2 years
IMPACT2 = storm_impact2()

class storm_impact3:
    
    new: float =(1 - 0.65) # young kelp growth > 1 year
    medium: float =(1 -0.55 )# kelp growth bet 1 to 2 years 
    mature: float =(1- 0.45) # kelp growth > 2 years
IMPACT3 = storm_impact3()



@dataclass(frozen=True)
class storm_phase:
    years: int
    storm_min_baseline: int
    storm_max_baseline: int
    strength_prob: np.ndarray

    # Creating a class blueprint for storm phases
    @classmethod
    def phase0(cls) -> "storm_phase":
        return cls(
            years=5,
            storm_min_baseline=5,
            storm_max_baseline=10,
            strength_prob=np.array([0.65, 0.25, 0.10])
        )

    @classmethod
    def phase1(cls) -> "storm_phase":
        return cls(
            years=10,
            storm_min_baseline=6,
            storm_max_baseline=11,
            strength_prob=np.array([0.60, 0.28, 0.12])
        )

    @classmethod
    def phase2(cls) -> "storm_phase":
        return cls(
            years=15,
            storm_min_baseline=7,
            storm_max_baseline=12,
            strength_prob=np.array([0.53, 0.32, 0.15])
        )

    @classmethod
    def phase3(cls) -> "storm_phase":
        return cls(
            years=20,
            storm_min_baseline=8,
            storm_max_baseline=13,
            strength_prob=np.array([0.45, 0.35, 0.20])
        )

# 2. Instantiating phase objects from the class blueprint
p0 = storm_phase.phase0()
p1 = storm_phase.phase1()
p2 = storm_phase.phase2()
p3 = storm_phase.phase3()

