import constants as c
import emission as em
import stocks as s
import radiative as r   
import validator as val
import data as dt
import co2_stocks as co2
import kelp as kp
import numpy as np
import storm as sto

def simulate_methane_engine (sector_list:list, fossil_fuel_list:list, params: dict, time_horizon: int):
    
    emissions  = []
    tot_emission = 0
    annual_emissions = np.zeros(time_horizon)
    ppb_ch4 = c.ch4parameters.ppb_ch4
    N2O_PPB = r.N2O_PPB_PROJECTION[:time_horizon] 
    current_N20_ppb = r.N2O_PPB_PROJECTION[0]

    #wetland 
    wetland = em.calc_wetland_emissions(time_horizon)
    annual_emissions+=wetland
    emissions.append(wetland)
    tot_emission+= np.sum(wetland)

    #sectors - animal_ag, paddy and landfills
    for sector in sector_list:
        sector_emission = em.calc_sector_emissions(sector, params[sector], time_horizon)
        annual_emissions+=sector_emission
        tot_emission+=np.sum(sector_emission)
        emissions.append(sector_emission)

    #fossil_fuel

    for fuel in fossil_fuel_list:
        fuel_emission = em.calc_fossil_fuel_emissions(fuel, params[fuel], time_horizon)
        annual_emissions+=fuel_emission
        tot_emission+=np.sum(fuel_emission)
        emissions.append(fuel_emission)

    #now call the superglu function to make a matrix from data.py
    matrix = np.vstack(emissions)

    #Calling the stock function 
    current_stock, oxidation_loss, ch4_stock_update, ch4_ppb_update = s.ch4_stock_update(annual_emissions, c.ch4parameters)
    print(ch4_ppb_update)
    co2_gain = co2.co2_from_ch4(oxidation_loss, co2.multi_factor)
    tot_co2 = np.round(np.sum(co2_gain),2)

    #calculate the radiative forcing and global warming potential
    #rf_ch4_array, rf_ch4, global_warming = r.calc_ch4_rf (ch4_ppb_update, r.N2O_PPB_PROJECTION )
    ch4_warming, rf_ch4  = r.calc_warming_petential_CH4(ch4_ppb_update, N2O_PPB, ppb_ch4, current_N20_ppb)
    return tot_emission, current_stock, tot_co2,  rf_ch4, ch4_warming
    sink = kelp

def simulate_kelp_growth_engine(time_horizon, ha, kelp_params, months=12):
    
    tot_co2_sink, annual_co2_sink, co2_removed_ppm = kp.kelp_growth_simulator(time_horizon, ha, kelp_params, months)
    #need to have the data function for annual_co2_sink
    return tot_co2_sink, co2_removed_ppm

def simulate_temp_drop_kelp(time_horizon, co2_params, co2_removed_ppm, lambda_sensitivity):
    delta = r.calc_radiative_forcing_co2(time_horizon, co2_params, co2_removed_ppm)
    cooling_potential = r.calc_cooling_potential_kelp(lambda_sensitivity, delta)
    return cooling_potential, delta

#wrapper

def kelp_co2_engine(time_horizon, ha, kelp_params, co2_params, lambda_sensitivity, months=12):
    tot_co2_sink, co2_removed_ppm = simulate_kelp_growth_engine(time_horizon, ha, kelp_params, months)
    cooling_potential_kelp, delta_radiative = simulate_temp_drop_kelp(time_horizon, co2_params, co2_removed_ppm, lambda_sensitivity)
    return  tot_co2_sink, cooling_potential_kelp, delta_radiative



if __name__ == "__main__":
    sector_list = c.sector_list
    fossil_fuel_list = c.fossil_fuel_list
    params = {
        "animal_ag": 0.0,
        "coal": 0.0,
        "oil": 0.0,
        "gas": 0.0,
        "landfills": 0.0,
        "paddy": -0.1,
        "shipping": 0.0,
        "flares": 0.1,
        "transport": 0.1,
        "kelp":100
    }
    time_horizon = 5
    

    total_emission, current_stock, tot_co2, tot_rf_ch4, global_warming = simulate_methane_engine(sector_list, fossil_fuel_list, params, time_horizon)
    print("Total Emission:", total_emission)
    ha= params["kelp"]
    
    co2_sink  = simulate_kelp_growth_engine(time_horizon, ha, kp.kelp_params, months=12)
    print("CO2 sink:", co2_sink)
    
