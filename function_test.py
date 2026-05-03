#Informed by International Energy Agency (IEA) outlooks and CH4 estimates from natural gas extraction, we can expect a moderate decline in emissions from natural gas extraction due to energy transition and methane capture technologies. This is a conservative estimate that accounts for both factors.
   
from methane.arctic_dashbord_6 import calc_annual_growth_rate, calc_emit_growth_rate


growth_rates = {
    "anima_ag": {"rate": 0.17, "years": 9},
    "landfill": {"rate": 0.5, "years": 25},
    "paddy": {"rate": 0.044, "years": 9},
}



rates = {
    "oxi_r": 0.083,
    "ppb_ch4": 1930,
    #Needs source checking
    "mt_to_ppb_co2": 0.128,  # Conversion factor from Mt CO₂ to ppm in the atmosphere (approximate)
    "mt_to_ppb_ch4": 0.35,  # Conversion factor from Mt CH₄ to ppb in the atmosphere (approximate)
    "ch4_to_co2_mass": 2.75,  # Molecular weight ratio (44/16)
}


fossil_fuel = {
    "coal": {
        1: {"years": 10, "rate": 0.2},
        2: {"years": 5, "rate": 0.05},
        3: {"years": 5, "rate": -0.01}
    },
    "oil": {
        1: {"years": 10, "rate": 0.15},
        2: {"years": 5, "rate": 0.03},
        3: {"years": 5, "rate": -0.005}

    },
    "gas": {
        1: {"years": 10, "rate": 0.25},
        2: {"years": 5, "rate": 0.1},
        3: {"years": 5, "rate": 0.0}
    }

}

ch4_enteric = ch4_emission["animal_agriculture"]
ch4_landfill = ch4_emission["landfills"]
ch4_paddy = ch4_emission["paddy"]
ch4_gas = ch4_emission["gas"]
ch4_oil = ch4_emission["oil"]
ch4_coal = ch4_emission["coal"]
ch4_wetlands = ch4_emission["wetlands"]

def calc_fossilfuel_emissions(t_slider, fuel_type):
                              
     """
     Calculate the total methane emissions from fossil fuel extraction over a specified time horizon, accounting for growth rates and oxidation.

     Parameters:
     - t_slider: A slider value representing the time horizon in years (0 to 20).
     - current_emission: The current methane emission level from fossil fuel extraction.
     - rates: A dictionary containing the oxidation rate under "oxi_r".

     Returns:
     - Total methane emissions from fossil fuel extraction over the specified time horizon, adjusted for oxidation.
     """
    
     yrs = 10 # use 10 years as the time horizon to calculate the growth rate.
     annual_rate = fuel_usgae_1[fuel_type] # use the predicted growth in coal usage to calculate the growth rate.
     current_emission = ch4_emissions[fuel_type]
     total = 0
     for _ in range(min(t_slider,10)):
        current_emission += current_emission * annual_rate
        total += current_emission
        total = total * (1 - rates["oxi_r"])
     if t_slider <= 10:
        return total

        # Calculate for the next 5 years.
                
                
     yrs = 5 # use 5 years as the time horizon to calculate the growth rate
     annual_rate = fuel_usgae_2[fuel_type]

     for _ in range(min(t_slider - 10, 5)):
            current_emission += current_emission * annual_rate
            total += current_emission
            total = total * (1 - rates["oxi_r"])
     if t_slider <= 15:
        return total
          
        # Calculate for the last 5 years.
     yrs = 5 # use 5 years as the time horizon to calculate the growth rate
     annual_rate = fuel_usgae_3[fuel_type] # use the predicted growth in coal usage to calculate the growth rate.
       
     for _ in range(t_slider - 15):
        current_emission += current_emission * annual_rate
        total += current_emission
        total = total * (1 - rates["oxi_r"])

     return total


def calc_fossil_emission_override (fossil_slider, t_slider, fossil_type):
    growth = calc_emit_growth_rate(fossil_slider, t_slider) 
    total = 0
    current_emission = ch4_emission[fossil_type] # the current emission is the baseline emission from fossil fuel, this is the starting point for calculating the growth in emissions from fossil fuel.
        
    for _ in range(t_slider):
        current_emission += current_emission* growth # each year the emission increases by the growth rate, this is the new emission for that year.
        total += current_emission # the new emission is added to the total additional emissions from coal
        total = total * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from coal emissions.

    return total



#These 2 functions should run together, one after the other 
def calc_annual_growth_rate(t_slider, growth_rate):
    # this function calculates the annual growth rate based on the time horizon (t_slider) and the growth rate for the sector. It returns the annual growth rate as a decimal.
    
    if t_slider == 0:
        return 0
    else:
        return growth_rate / t_slider
 

def clac_BAU_emission (t_slider, sector, emission_type, oxi_rates, mt_to_ppb, growth_rate):
# before running emsion_change_BAU_calc, make sure to run calc_annual_growth_rate first to get the growth rate for the sector, then use that growth rate as an input in emission_change_BAU_calc.
# this function calculates the change in emissions from a specific sector (e.g., fossil fuel, animal agriculture) over a specified time horizon (t_slider) under a business-as-usual (BAU) scenario, accounting for growth rates and oxidation. It returns the total emissions, the change in parts per billion (ppb), and the carbon addition to the atmosphere.
    if t_slider == 0:
        return 0, 0, 0, 0
    
    current_emission = emission_type
    total = 0
    delta_ppb = 0
    co2_addition = 0
    growth = calc_annual_growth_rate(t_slider, growth_rate) # calculate the annual growth rate based on the time horizon and the growth rate for the sector.

    for _ in range (t_slider):
        current_emission +=current_emission*growth
        total+=current_emission
        total = total * (1- rates["oxi_r"]) # could I combine the 2 total lines
        delta_ppb +=current_emission/rates["ppb_ch4"]
        carbon_addition+=(total* rates[oxi_r]) * 2.5
    return total, delta_ppb, carbon_addition


def calc_ch4_a_ag(t_slider, animal_ag_slider):
    """
    t_slider: number of years
    animal_ag_slider: fractional total change (e.g., -50% = -0.5)
    oxi_r: oxidation rate (fraction)
    Methane oxidation is treated as a first-order continuous decay process with lifetime τ.
    The model uses yearly timesteps with exponential decay to approximate continuous atmospheric chemistry.
    
    Returns:
        atmospheric CH₄ contribution from animal agriculture over t_slider years, with growth and oxidation applied
    """

    #calculate annual growth rate
    #annual_rate = calc_emit_growth_rate(animal_ag_slider, t_slider)
    
    if t_slider == 0: 
        return 0
    if animal_ag_slider == 0:
        yrs = 9 # use 9 years as the time horizon to calculate the growth rate since the predicted growth is for 2034 and prediction made in 2025.
        rate = 0.17 # use the predicted growth in animal ag to calculate the growth rate.
        #initialize varilbles used in the for loop.
        total = 0
        delta_ppb = 0 #for ppb calculation
        current_emission = emission_type # the current emission is the baseline emission from animal agriculture, this is the starting point for calculating the growth in emissions from animal agriculture.
        growth = calc_annual_growth_rate(yrs, rate) # use the predicted growth in animal ag to calculate the annual growth rate.
        
        for _ in range(t_slider):
            
            current_emission += current_emission* growth # each year the emission increases by the growth rate, this is the new emission for that year.
            total += current_emission # the new emission is added to the total additional emissions from animal
            total = total * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from animal ag emissions.
            delta_ppb += total/rates["ppb_ch4"]
        return total, delta_ppb
    else:
        growth = calc_emit_growth_rate(animal_ag_slider, t_slider) 
        total = 0
        delta_ppb = 0 #for ppb calculation
        current_emission = ch4_emission["animal_agriculture"] # the current emission is the baseline emission from animal agriculture, this is the starting point for calculating the growth in emissions from animal agriculture.
        #current_emission = ch4_emission["animal_agriculture"]+  ch4_emission["animal_agriculture"]* growth
        for _ in range(t_slider):
            current_emission += current_emission* growth # each year the emission increases by the growth rate, this is the new emission for that year.
            total += current_emission # the new emission is added to the total additional emissions from animal
            total = total * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from animal ag emissions.
            delta_ppb += total/rates["ppb_ch4"]
        return total, delta_ppb
    
def calc_fossilfuel_emissions_bau(t_slider, fuel_type):
    """
     Calculate the total methane emissions from fossil fuel extraction over a specified time horizon, accounting for growth rates and oxidation.

     Parameters:
     - t_slider: A slider value representing the time horizon in years (0 to 20).
     - current_emission: The current methane emission level from fossil fuel extraction.
     - rates: A dictionary containing the oxidation rate under "oxi_r".

     Returns:
     - Total methane emissions from fossil fuel extraction over the specified time horizon, adjusted for oxidation.
     """
    #calc_BAU_emission_fuel(t_slider, "coal", 1) this is the function call for testing, it should return the total emissions from coal extraction over 10 years with a growth rate of 20% per year.
    #fuel =fossil_fuel[fuel_type]
    if t_slider == 0:
        return 0,0,0,0
    
    # initialize the total additional emissions from fossil fuel to 0, this variable will be updated each year with the new emissions from fossil fuel extraction.
    fuel_ch4, ch4_stocks_fule, co2_added, ch4_ppb_fuel, co2_ppb_fuel = 0, 0, 0, 0, 0
    current_emission = ch4_emission[fuel_type] # the current emission is the baseline emission from fossil fuel, this is the starting point for calculating the growth in emissions from fossil fuel.
    
    # --- PHASE 1: Years 1 to 10 ---
    phase = 1
    p1 = 10 # use 10 years as the time horizon to calculate the growth rate for phase 1.
    years_p1 = min(t_slider, p1) # calculate the number of years in phase 1 based on the time slider
    growth_rate1 = fossil_fuel[fuel_type][phase]["rate"] # get the growth rate for phase 1 from the fossil fuel data
    for _ in range(years_p1):
        current_emission += current_emission * growth_rate1 # each year the emission increases by the growth rate for phase 1, this is the new emission for that year.
        fuel_ch4 += current_emission # the new emission is added to the total additional emissions from fossil fuel
        ch4_stocks_fule = fuel_ch4 * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from fossil fuel emissions.
        oxidized_ch4 = fuel_ch4 * rates["oxi_r"] # calculate the amount of CH4 that is oxidized each year based on the oxidation rate.
        co2_added += (oxidized_ch4) * 2.5 # calculate the CO2 added to the atmosphere from the oxidized CH4, using the molecular weight ratio of 2.5.
        fuel_ch4 -= oxidized_ch4 # subtract the oxidized CH4 from the total CH4 to get the new total CH4 in the atmosphere after accounting for oxidation.
    
    if t_slider > 10:
        # --- PHASE 2: Years 11 to 15 ---
        phase = 2
        p2 = 5 # use 5 years as the time horizon to calculate the growth rate for phase 2.
        years_p2 = min(t_slider - p1, p2) # calculate the number of years in phase 2 based on the time slider
        growth_rate2 = fossil_fuel[fuel_type][phase]["rate"] # get the growth rate for phase 2 from the fossil fuel data
        for _ in range(years_p2):
            current_emission += current_emission * growth_rate2 # each year the emission increases by the growth rate for phase 2, this is the new emission for that year.
            fuel_ch4 += current_emission # the new emission is added to the total additional emissions from fossil fuel
            ch4_stocks_fule = fuel_ch4 * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from fossil fuel emissions.
            oxidized_ch4 = fuel_ch4 * rates["oxi_r"] # calculate the amount of CH4 that is oxidized each year based on the oxidation rate.
            co2_added += (oxidized_ch4) * 2.5 # calculate the CO2 added to the atmosphere from the oxidized CH4, using the molecular weight ratio of 2.5.
            fuel_ch4 -= oxidized_ch4 # subtract the oxidized CH4 from the total CH4 to get the new total CH4 in the atmosphere after accounting for oxidation.
    
    if t_slider > 15:
        phase = 3
         # --- PHASE 3: Years 16 to 20 ---
        p3 = 5 # use 5 years as the time horizon to calculate the growth
            # rate for phase 3.
        years_p3 = min(t_slider - 15, p3) # calculate the number of years in phase 3 based on the time slider
        growth_rate3 = fossil_fuel[fuel_type][phase]["rate"] # get the growth rate for phase 3 from the fossil fuel data
        for _ in range(years_p3):
            current_emission += current_emission * growth_rate3 # each year the emission increases by the growth rate for phase 2, this is the new emission for that year.
            fuel_ch4 += current_emission # the new emission is added to the total additional emissions from fossil fuel
            ch4_stocks_fule = fuel_ch4 * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from fossil fuel emissions.
            oxidized_ch4 = fuel_ch4 * rates["oxi_r"] # calculate the amount of CH4 that is oxidized each year based on the oxidation rate.
            co2_added += (oxidized_ch4) * 2.5 # calculate the CO2 added to the atmosphere from the oxidized CH4, using the molecular weight ratio of 2.5.
            fuel_ch4 -= oxidized_ch4 # subtract the oxidized CH4 from the total CH4 to get the new total CH4 in the atmosphere after accounting for oxidation.
    
    ch4_ppb_fuel = ch4_stocks_fule / rates["ppb_ch4"] # calculate the change in parts per billion (ppb) of CH4 in the atmosphere from the total additional emissions from fossil fuel, using the conversion factor from Mt CH4 to ppb. 
    co2_ppb_fuel = co2_added / rates["mt_to_ppb_co2"] # calculate the change in parts per billion (ppb) of CO2 in the atmosphere from the total CO2 added, using the conversion factor from Mt CO2 to ppm.
    return ch4_stocks_fule, co2_added, ch4_ppb_fuel, co2_ppb_fuel



def calc_fossil_emission_override (fossil_slider, t_slider, fossil_type):
    
    fuel_ch4, ch4_stocks_fule, co2_added, ch4_ppb_fuel, co2_ppb_fuel = 0, 0, 0, 0, 0
    current_emission = ch4_emission[fuel_type] # the current emission is the baseline emission from fossil fuel, this is the starting point for calculating the growth in emissions from fossil fuel.
    
    if t_slider == 0:
        return 0,0,0,0
    growth = calc_emit_growth_rate(fossil_slider, t_slider)
    total = 0
    current_emission = ch4_emission[fossil_type] # the current emission is the baseline emission from fossil fuel, this is the starting point for calculating the growth in emissions from fossil fuel.
    for _ in range(t_slider):
        fuel_ch4 += current_emission * growth # the new emission is added to the total additional emissions from fossil fuel
        ch4_stocks_fule = fuel_ch4 * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from fossil fuel emissions.
        oxidized_ch4 = fuel_ch4 * rates["oxi_r"] # calculate the amount of CH4 that is oxidized each year based on the oxidation rate.
        co2_added += (oxidized_ch4) * ch4_to_co2_mass # calculate the CO2 added to the atmosphere from the oxidized CH4, using the molecular weight ratio of 2.5.
        fuel_ch4 -= oxidized_ch4

    co2_ppb_fuel = co2_added / rates["mt_to_ppb_co2"] # calculate the change in parts per billion (ppb) of CO2 in the atmosphere from the total CO2 added, using the conversion factor from Mt CO2 to ppm.
    ch4_ppb_fuel = ch4_stocks_fule / rates["ppb_ch4"] # calculate the change in parts per billion (ppb) of CH4 in the
    return ch4_stocks_fule, co2_added, ch4_ppb_fuel, co2_ppb_fuel


def calc_sector_emission_bau (t_slider, sector):
    if t_slider == 0:
        return 0,0,0,0
    #calculate the emission rate, based on the prediction
    
    
    # Access the global dictionary
    growth  = growth_rates[sector]["rate"]# get the growth rate for the sector from the growth rates data
    yrs = growth_rates[sector]["years"] # get the time horizon for the growth rate from the growth rates data
    annual_rate = calc_annual_growth_rate(yrs, growth) # calculate the annual growth rate based on the time horizon and the growth rate for the sector.
    
    # Initializing  accumulators
    current_emission = ch4_emission[sector] # the current emission is the baseline emission from the sector, this is the starting point for calculating the growth in emissions from the sector.
    ch4_stocks_sector, co2_added,  = 0, 0
    
    for _ in range(t_slider):
        current_emission *= (1 + annual_rate) # the new emission is added to the total additional emissions from fossil fuel
        ch4_stocks_sector += current_emission * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from fossil fuel emissions.
        oxidized_ch4 = current_emission * rates["oxi_r"] # calculate the amount of CH4 that is oxidized each year based on the oxidation rate.
        co2_added += (oxidized_ch4) * ch4_to_co2_mass # calculate the CO2 added to the atmosphere from the oxidized CH4, using the molecular weight ratio of 2.5.
        ch4_stocks_sector -= oxidized_ch4 
    
    co2_ppb_sector = co2_added / rates["mt_to_ppb_co2"] # calculate the change in parts per billion (ppb) of CO2 in the atmosphere from the total CO2 added, using the conversion factor from Mt CO2 to ppm.
    ch4_ppb_sector = ch4_stocks_sector / rates["ppb_ch4"] # calculate the change in parts per billion (ppb) of CH4 in the
    
    return ch4_stocks_sector, co2_added, ch4_ppb_sector, co2_ppb_sector


def calc_sector_emission_override(t_slider, sector, sector_slider):
    if t_slider == 0 or sector_slider == 0:
        return 0, 0, 0, 0
    
    # Initialize variables from global data
    yrs = t_slider
    growth = sector_slider
    annual_rate = calc_annual_growth_rate(yrs, growth)
    
    # Initialize local variables
    current_emission = ch4_emission[sector] 
    ch4_stocks_sector = 0
    co2_added = 0

    for _ in range(t_slider):
        # Apply the user-defined growth/reduction rate
        current_emission *= (1 + annual_rate) 
        
        # Add yearly flow to the atmospheric stock
        ch4_stocks_sector += current_emission
        
        # Calculate oxidation on the TOTAL stock
        oxidized_this_year = ch4_stocks_sector * rates["oxi_r"]
        
        # Mass balance: convert oxidized CH4 to CO2
        co2_added += oxidized_this_year * ch4_to_co2_mass
        
        # Remove the oxidized portion from the methane stock
        ch4_stocks_sector -= oxidized_this_year
    
    # 3. Final conversion to concentrations
    co2_ppb_sector = co2_added / rates["mt_to_ppb_co2"]
    ch4_ppb_sector = ch4_stocks_sector / rates["ppb_ch4"]
    
    return ch4_stocks_sector, co2_added, ch4_ppb_sector, co2_ppb_sector