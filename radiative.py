import constants as c

import stocks as s
import pandas as pd
import numpy as np
from dataclasses import dataclass

#Methane radiative forcing -- Etminan et al. 2016 (GRL, doi:10.1002/2016GL071930)
# Table 1 simplified expression, as adopted by IPCC AR6.
# RF_CH4 = (a3*Mbar + b3*Nbar + d3) * (sqrt(M) - sqrt(M0))


ch4_params = c.ch4parameters()
rf_params = c.radiative_forcing()

M0 = rf_params.CH4_PPB_M0 # historical pre-industrial methane concentration in ppb (1850)
RF_CONSTANT = rf_params.RF_CONSTANT
N0 = rf_params.N2O_REF_PPB #radiative efficiency constant Myhre et al and updated by IPCC assessment reports.
N2O_PPB_PROJECTION : np.array = np.array([337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348,349,350, 351, 352, 353,354,355, 356])# N2O concentrations in ppb for the years 2025-2045 (example values, informed by historical trends and projections from sources like NOAA and IPCC reports)lambda : float = rf_params.lambda  # Climate sensitivity parameter (W/m² per °C)
lambda_sensitivity = rf_params.lambda_sensitivity  # Climate sensitivity parameter (W/m² per °C)    

 
A3 = -1.3e-6
B3 = -8.2e-6
D3 = 0.043
mid = 0.5


#Mbar = 0.5*(M + M0)  # mean of current & pre-industrial CH4 (ppb)
#Nbar = 0.5*(N + N0)   #mean of current & pre-industrial N2O (ppb)
def calc_ch4_rf(ch4_ppb:np.array, N2O_PPB_PROJECTION:np.array):
    Mbar = (ch4_ppb + M0) * mid
    Nbar = (N2O_PPB_PROJECTION + N0) * mid
    n = len(ch4_ppb)
    Nbar = Nbar[:n]
    rf_ch4 = (A3 * Mbar + B3 * Nbar + D3) * (np.sqrt(ch4_ppb) - np.sqrt(M0))
    earth_warming = rf_ch4[-1] * rf_params.lambda_sensitivity  # Calculate the warming effect based on the last year's radiative forcing
    
    return rf_ch4, rf_ch4[-1], earth_warming


N20_PPB_current = N2O_PPB_PROJECTION[0]  # Assuming the first value corresponds to the current year
def calc_ch4_warming_current(ch4_ppb_current:float, N2O_PPB_current:float):

    Mbar = (ch4_ppb_current + M0) * mid
    Nbar = (N2O_PPB_current+N0) * mid
    rf_ch4_now = (A3 * Mbar + B3 * Nbar + D3) *(np.sqrt(ch4_ppb_current)- np.sqrt(M0))
    current_earth_warming = rf_ch4_now * rf_params.lambda_sensitivity
    rf_ch4_now = rf_ch4_now.item()  # Convert to a scalar if it's a single-element array
    return rf_ch4_now, current_earth_warming


# Wrapper function
# Calculat the current warming potential from CH4

#def calc_warming_petential_CH4(ch4_ppb:np.array, N2O_PPB_PROJECTION:np.array, ch4_ppb_current:float, N2O_PPB_current:float):
   # rf_ch4, rf_ch4[-1], tot_warming = calc_ch4_rf(ch4_ppb, N2O_PPB_PROJECTION)
   # rf_ch4_now, current_warming = (ch4_ppb_current, N2O_PPB_current)
   # projected_warming = tot_warming - current_warming
   # projected_rf_ch4 = rf_ch4 - rf_ch4_now
    #return  projected_warming, projected_rf_ch4

def calc_warming_petential_CH4(ch4_ppb, N2O_PPB_PROJECTION, ch4_ppb_current, N2O_PPB_current):
    rf_ch4, rf_last, tot_warming = calc_ch4_rf(ch4_ppb, N2O_PPB_PROJECTION)
    rf_ch4_now, current_warming = calc_ch4_warming_current(ch4_ppb_current, N2O_PPB_current)

    projected_warming = tot_warming - current_warming
    projected_rf_ch4 = rf_ch4 - rf_ch4_now
    projected_rf_ch4 = projected_rf_ch4[-1]  # Get the last value
    
    return projected_warming, projected_rf_ch4
