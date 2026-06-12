import constants as c

import stocks as s
import pandas as pd
import numpy as np
from dataclasses import dataclass



ch4_params = c.ch4parameters()
rf_params = c.RadiativeForcing()

M0 = rf_params.CH4_PPB_M0 # historical pre-industrial methane concentration in ppb (1850)
RF_CONSTANT = rf_params.RF_CONSTANT
N0 = rf_params.N2O_REF_PPB #radiative efficiency constant Myhre et al and updated by IPCC assessment reports.
OVERLAP_SCALE: float = rf_params.CH4_N2O_OVERLAP_SCALE
N20_PPB_PROJECTION : list = [337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348,349,350, 351, 352, 353,354,355, 356] # N2O concentrations in ppb for the years 2025-2045 (example values, informed by historical trends and projections from sources like NOAA and IPCC reports)
H2O_SCALE: float = rf_params.H2O_FEEDBACK_SCALE

C0 = 1
C1 = 2.01 * 10**-5
C2 = 0.75
C3 = 5.31 * 10**-15
C4 = 1.52
F_overlap_preindustrial = OVERLAP_SCALE*np.log(C0+ (C1*(M0*N0)**C2+C3*M0*(M0*N0)**C4))

#DIRECT BLOCK
def calc_ch4_rf_base (ch4_ppb_list:list, M0: float, RF_CONSTANT: float):
    """
    
    Methane radiative forcing (baseline formulation only, no N2O, H20 overlap correction in this function).

Uses:

RF = rf_constant * (sqrt(M) - sqrt(M0))
    
    Parameters:
    ch4_ppb (list): A list of methane concentrations in ppb.
    M0 (float): The baseline methane concentration in ppb.
    rf_constant (float): The radiative efficiency constant for methane (W/m² per ppb).
    
    Returns:
    list: A list of square root values of the difference between current and baseline methane concentrations.
    """
   
    # the first step for calculating the radiative forcing using the formula: 0.036 * (sqrt(M1) - sqrt(M0))
    RF_0 = [RF_CONSTANT * (np.sqrt(M1) - np.sqrt(M0)) for M1 in ch4_ppb_list]
    RF_0 = np.array(RF_0)
    return RF_0

    # Calculate the N2O adjustment factor using the formula: N2O_adjustment = 0.12 * (sqrt(N2O_ppb) - sqrt(N0))
    

#PRESENT OVERLAP

def overlap_calculation(N20_PPB_PROJECTION: list, ch4_ppb_list: list):
    """
    Calculate the N2O adjustment factor based on its concentration in parts per billion (ppb).
    
    Parameters:
    N2O_ppb (list): A list of N2O concentrations in ppb.
    CH4_PPB_list (list): A list of methane concentrations in ppb, used for potential future adjustments if needed.
    N0 (float): The baseline N2O concentration in ppb.
    adjustment_constant (float): The constant used for adjusting the radiative forcing based on N2O concentration.
    
    Returns:
    list: A list of N2O adjustment factors.
    """
    
    ch4_ppb_list = np.array(ch4_ppb_list)
    n= len(ch4_ppb_list)
    N20_PPB_PROJECTION = np.array(N20_PPB_PROJECTION)
    N20_PPB_adjusted = N20_PPB_PROJECTION[:n]
    overlap_correction = OVERLAP_SCALE * np.log(C0 + (C1 * (ch4_ppb_list * N20_PPB_adjusted)**C2 + C3 * ch4_ppb_list * (ch4_ppb_list * N20_PPB_adjusted)**C4))
    
    
    #for ch4_element,N20_element in CH4_PPB_list, N20_PPB_PROJECTION:
       # overlap_correction.append(OVERLAP_SCALE*np.log(C0+ (C1*(ch4_element*N20_element)**C2+C3*ch4_element*(ch4_element*N20_element)**C4)))
    return overlap_correction
    


def overlap_correction_2(overlap_correction:list, F_overlap_preindustrial:float):
    overlap_correction = np.array(overlap_correction)
    result  = overlap_correction - F_overlap_preindustrial
    return result 

    #result = [(element- F_overlap_preindustrial) for element in overlap_correction]
    #return result  


#Wrapper function
def calc_RF_CH4 (ch4_ppb_list, M0, RF_CONSTANT,N20_PPB_PROJECTION,H20_SCALE ):
    
    
    ch4_ppb_adjusted_M0  = calc_ch4_rf_base (ch4_ppb_list, M0, RF_CONSTANT)
    N20_PPB_adjustment_fac = overlap_calculation(N20_PPB_PROJECTION, ch4_ppb_list)
    net_penalty = overlap_correction_2(N20_PPB_adjustment_fac, F_overlap_preindustrial)
    rf_sans_h2o = ch4_ppb_adjusted_M0 - net_penalty 
    tot_rf = rf_sans_h2o * H20_SCALE
    return tot_rf



#def calc_radiative_forcing_ch4(current_ppb_ch4: float):
#if __name__ == "__main__":
    # Example usage of the calc_radiative_forcing_ch4 function
    