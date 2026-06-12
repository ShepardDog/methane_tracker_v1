

## MODEL ASSUMPTIONS
 # - Time is modeled in yearly timesteps
 # - Each timestep represents end-of-year state
 # -  Within each year, oxidation acts on existing stock, then new emissions are added

 # - Methane oxidation is approximated as a constant fractional decay
 # - Source contributions are modeled independently and summed

## Methane Modeling Approach
 #- countinious growth model
 # Paddy and animal ag growth are modeled using exponential extrapolation of the
# 9-year predicted growth rates to the full simulation horizon.

# ---------------------
# 1. Imports
# -------------------------
#from hmac import trans_36
#rom itertools import accumulate

import math
import textwrap
import numpy as np
import pandas as pd
import constants as c

from constants import (
  
    
    fossil_fuel,
    base_line,
    rates
)


def calc_growth_rate( sector: str,emission_adjusement: float, time_horizon: int):
    #If emission_adjustment is 0, return continuous growth rate for a sector from a growth_rate lookup dictionary. 
    # Otherwise, override the BAU values with emission_adjustment.
    # Usage:
    #animal_ag_growth_rate  = calc_growth_rate("animal_ag", animal_ag_slider, t_slider) 
    if time_horizon == 0:
        return 0
    if emission_adjusement == 0:
        # BAU model.
        years = c.growth_rates[sector]["years"]
        growth = c.growth_rates[sector]["rate"]
        return math.log(1 + growth) / years
    
    else:
        # Adjusted model. Override the BAU values with emission_adjustment.
        
        years = time_horizon
        growth = emission_adjusement
        if growth == -1:
            growth = -0.99
            return math.log(1 + growth) / years
        else: 
            return math.log(1 + growth) / years
        
def calc_wetland_emissions(time_horizon: int):  
#for v1 version of the app we will assume that wetland emissions remain constant over time, but for v2 wetland emission will be considered as a function of temprature and time.
    if time_horizon == 0 :
        return np.zeros(0, dtype=float)
    
    else:
    #Calculates natural wetland emissions. 
    #v1: Constant time list. 
    #v2: Will integrate temperature_data loops seamlessly here.
   
        base_emission = c.ch4_emission.get("wetlands", 0.0)
        emissions = np.full(time_horizon, base_emission, dtype=float)
        return np.round(emissions, 2)
        
           
        
def project_humane_phaseout(time_horizon: int):
    #Calculating the maximum possible emission reduction from animal ag
    #Assumptions: the current herd is young between 5- 6 years old and the emission will tapper with in a period of 20 years, this takes into conideration the young calves born now.
    # assumptions : the graph will take the shape of  E(t) = 120. (1-(x/20)**2), where a is the slider value, h is the time horizon and k is the current emission level.
    
    max_time  = 20
    base_emission = c.ch4_emission["animal_ag"]
    power = 2
    emissions_humane = []
    for t in range(time_horizon):
        em = base_emission * (1 - (t/max_time)**power)
        
        emissions_humane.append(em)
    emissions_humane = np.round(np.array(emissions_humane), 2)
    return np.sum(emissions_humane), emissions_humane
          
        
def calc_sector_emissions( sector: str, emission_adjustment: float, time_horizon: int):
    
    if time_horizon == 0 :
        return np.zeros(0, dtype=float) 
    
    if sector == "animal_ag" and emission_adjustment < 0: 
        
        E0 = c.ch4_emission[sector]
        growth_rate = calc_growth_rate(sector, emission_adjustment, time_horizon)
        
        emissions = [E0 * math.exp(growth_rate * t) for t in range(time_horizon)]
        emissions = np.array(emissions)
        emissions_best_case, bestcase_list  = project_humane_phaseout(time_horizon)
        if emissions_best_case > sum(emissions):
            return np.round(bestcase_list, 2)
        else:
            return np.round(emissions, 2)
    
    else :  
        E0 = c.ch4_emission[sector]
        growth_rate = calc_growth_rate(sector, emission_adjustment, time_horizon)
        emissions = [E0 * math.exp(growth_rate * t) for t in range(time_horizon)]
        return np.round(np.array(emissions), 2)     


#Calculating fossil fuel growth rates 
def calc_fossil_fuel_emissions (fuel:str, emission_adjustement: float, time_horizon: int):
    if time_horizon == 0 :
        return np.zeros(0, dtype=float)
#Calculate BAU senario 
    if emission_adjustement == 0:
        df = fossil_fuel.set_index(["fuel", "phase"])
        
        # --- BASELINE (Year 1) ---
        E_base = c.ch4_emission[fuel]
        emissions = [E_base]
        
        # --- PHASE 1 (Up to Year 10) ---
        rate_1 = df.loc[(fuel, 1), "rate"]
        p1 = df.loc[(fuel, 1), "years"] 
        
        # Calculate exactly how many steps Phase 1 needs to fill up to Year 10
        years_p1 = min(time_horizon, p1) 
        phase1_emissions = [E_base * math.exp(rate_1 * t) for t in range(1, years_p1)]
        emissions.extend(phase1_emissions)

        if len(emissions) >= time_horizon:
            #return [round(val, 2) for val in emissions[:time_horizon]]
            return np.round(np.array(emissions[:time_horizon]), 2)
        
        # --- PHASE 2 (Up to Year 15) ---
        rate_2 = df.loc[(fuel, 2), "rate"]
        p2 = df.loc[(fuel, 2), "years"] 
        
        # Dynamically calculate remaining steps left for Phase 2 based on current array size
        years_p2 = min(time_horizon - len(emissions), p2)
        E_phase2_initial = emissions[-1] # Clean handover from the true end of Phase 1
        
        phase2_emissions = [E_phase2_initial * math.exp(rate_2 * t) for t in range(1, years_p2 + 1)]
        emissions.extend(phase2_emissions)
        
        if len(emissions) >= time_horizon:
            #return [round(val, 2) for val in emissions[:time_horizon]]
            return np.round(np.array(emissions[:time_horizon]), 2)
        
        # --- PHASE 3 (Up to Year 20) ---
        rate_3 = df.loc[(fuel, 3), "rate"]
        p3 = df.loc[(fuel, 3), "years"] 
        
        # Dynamically fill whatever empty slots are left up to the time horizon limit
        years_p3 = min(time_horizon - len(emissions), p3)
        E_phase3_initial = emissions[-1] # Clean handover from the true end of Phase 2
        
        phase3_emissions = [E_phase3_initial * math.exp(rate_3 * t) for t in range(1, years_p3 + 1)]
        emissions.extend(phase3_emissions)
        
        # Returns exactly the time_horizon length with clean 2-decimal rounding
        #return [round(val, 2) for val in emissions[:time_horizon]]
        return np.round(np.array(emissions[:time_horizon]), 2)

#Calculate emission based on user provided rates 
#     
    else:
        #Calculate the fuel emission rate 
        rate = calc_growth_rate(fuel, emission_adjustement, time_horizon)
        E0 = c.ch4_emission[fuel]
     
        emissions = [E0 * math.exp(rate * t) for t in range(time_horizon)]
        
        return np.round(np.array(emissions), 2)
    
#def total_emissions( emissions_sector: np.ndarray, emissions_fossil_fuel: np.ndarray, emissions_wetland: np.ndarray):
   # total_array = emissions_sector + emissions_fossil_fuel + emissions_wetland
    #sum_total = np.sum(total_array)
    #return sum_total


def total_emissions(emissions_sector, emissions_fossil_fuel, emissions_wetland):
    emissions_sector = np.array(emissions_sector, dtype=float)
    emissions_fossil_fuel = np.array(emissions_fossil_fuel, dtype=float)
    emissions_wetland = np.array(emissions_wetland, dtype=float)

    total_array = emissions_sector + emissions_fossil_fuel + emissions_wetland
    return np.sum(total_array)


 
if __name__ == "__main__":
    # Example usage of the functions
    time_horizon = 20
    animal_ag_growth_rate  = calc_growth_rate("animal_ag", 0.0, time_horizon)
    #print(f"Animal Agriculture Growth Rate: {animal_ag_growth_rate}")
    
    #wetland_emissions = calc_wetland_emissions(time_horizon)
    #print(f"Wetland Emissions: {wetland_emissions}")
    
    animal_ag_emissions = calc_sector_emissions("animal_ag", 0.0, time_horizon)
    print(f"Animal Agriculture Emissions: {animal_ag_emissions}")

    #paddy_growth_rate  = calc_growth_rate("paddy", 0.0, time_horizon)
    #paddy_emissions = calc_sector_emissions("paddy", paddy_growth_rate, time_horizon)
    #print(f"Paddy Emissions: {paddy_emissions}")
    
    #fossil_fuel_emissions = calc_fossil_fuel_emissions("oil", 0.0, time_horizon)
    #print(f"Fossil Fuel Emissions: round ({fossil_fuel_emissions})")
    landfill_growth_rate  = calc_growth_rate("landfills", 0.0, time_horizon)
    landfill_emissions = calc_sector_emissions("landfills", 0.0, time_horizon)
    print(f"Landfill Emissions: {landfill_emissions}")
    #total_emissions = total_emissions(np.array(animal_ag_emissions), np.array(fossil_fuel_emissions), np.array(wetland_emissions))
    #print(f"Total Emissions: {total_emissions}")