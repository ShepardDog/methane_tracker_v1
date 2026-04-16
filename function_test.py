#Informed by International Energy Agency (IEA) outlooks and CH4 estimates from natural gas extraction, we can expect a moderate decline in emissions from natural gas extraction due to energy transition and methane capture technologies. This is a conservative estimate that accounts for both factors.
   
from methane.arctic_dashbord_6 import calc_annual_growth_rate, calc_emit_growth_rate


fuel_usgae_1 ={
    "coal": -0.005, 
    "oil": 0.003, 
    "gas": 0.015  
}
fuel_usgae_2 ={
    "coal": -0.01, 
    "oil": 0.0, 
    "gas": 0.005  
}

fuel_usgae_3 ={
    "coal": -0.01, 
    "oil": -0.005, 
    "gas": 0.0  
}

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



def emission_change_BAU_calc (t_slider, sector, CH4_emission[section], rates[oxi_r], rates[mt_to_ppb]):

    current_emission = animal_ag[sector]
    total = 0
    delta_ppb = 0
    carbon_addition = 0


    for _ in range (t_slider):
        current_emission +=current_emission*growth
        total+=current_emission
        total = total * (1- rates["oxi_r"]) # could I combine the 2 lines
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
        current_emission = ch4_emission["animal_agriculture"] # the current emission is the baseline emission from animal agriculture, this is the starting point for calculating the growth in emissions from animal agriculture.
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
                    