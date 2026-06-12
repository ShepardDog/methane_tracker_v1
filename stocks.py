

import constants as c
import emission as em
from dataclasses import dataclass


current_ppb_ch4 = c.base_line["ch4_ppb"]
current_ppb_co2 = c.base_line["co2_ppb"]
ch4_ppb_conv = c.rates["mt_to_ppb_ch4"]
co2_ppb_conv = c.rates["mt_to_ppb_co2"] 


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
    ch4_ppb_update = [parameters.ppb_ch4]
    
    
    
    for annual in annual_emissions:
        #calculte the oxidation rate for the current stock of methane.
       # print(f"emission this year: {annual}, current_stock before: {current_stock}")
        oxidation_rate_ch4 = calc_ch4_oxidation_rate(parameters, current_stock)
        oxidation_loss.append(current_stock * oxidation_rate_ch4)
        current_stock = current_stock*(1 - oxidation_rate_ch4)
        current_stock += annual
        ch4_stock_update.append(current_stock)
        ch4_ppb_update.append(current_stock * ch4_ppb_conv)
    
    return current_stock, oxidation_loss, ch4_stock_update, ch4_ppb_update



if __name__ == "__main__":
    ch4_new, oxi_loss, ch4_now, ch4_ppb = ch4_stock_update ([1,2,3,4,5],c.ch4parameters)
    print (ch4_new)
    print (oxi_loss)
    print(ch4_now)
    print(ch4_ppb)
     

        
   