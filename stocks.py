

import constants as c
import emission as em
from dataclasses import dataclass





def calc_ch4_oxidation_rate(parameters: c.ch4parameters, current_stock: float):
    # Calculates the methane oxidation rate based on the current stock and a sensitivity coefficient.
    # The function will return the oxidation rate for methane, which can be used to update the methane stock.
    # 
    # CRITICAL NOTE ON THE SENSITIVITY COEFFICIENT (s): 
    # A higher value of s means a STRONGER chemical feedback (more OH depletion). 
    # This means the lifetime stretches out longer, causing the oxidation rate to increase 
    # MORE SLOWLY as the methane stock increases.
    
    ch4_life_time = parameters.ref_tau * (current_stock / parameters.ref_stock) ** parameters.sensitivity_coefficient
    oxidation_rate_ch4 = 1 / ch4_life_time
    return oxidation_rate_ch4



def ch4_stock_update(annual_emissions: list, parameters: c.ch4parameters):
    #notes to self:
    #Oxidation is computed from the pre‑decay CH₄ stock (physically standard timing
    #when calling the function pass the parameters as a dataclass and the annual emissions as a list of emissions for each year.
    #and the emissions list should be the output of the calc_ch4_emissions function in emission.py
    #the function will return the updated stock of methane  and it will also  return oxidized CH4 fot the CO2 engine 
    
    oxidation_loss = []
    current_stock = parameters.ref_stock
    
    ch4_stock_update = [current_stock]
    for _ in annual_emissions:
        #calculte the oxidation rate for the current stock of methane.
        oxidation_rate_ch4 = calc_ch4_oxidation_rate(parameters, current_stock)
        oxidation_loss.append(current_stock * oxidation_rate_ch4)
        current_stock = current_stock*(1 - oxidation_rate_ch4)
        current_stock += _
        ch4_stock_update.append(current_stock)
    
    return current_stock, oxidation_loss, ch4_stock_update
        
   