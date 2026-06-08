import numpy as np
import pandas as pd
import constants as c
import emission as em
import stocks as s




ch4 = c.base_line["ch4"]
co2 = c.base_line["co2"]
ch4_ppb = c.base_line["ch4_ppb"]
co2_ppb = c.base_line["co2_ppb"]
new_ch4 = c.new_emissions["ch4"]
new_co2 = c.new_emissions["co2"]

#offset values
co2_p = c.offsets["co2_p"]
ch4_p = c.offsets["ch4_p"]
temp_p = c.offsets["temp_p"]
ice_p = c.offsets["ice_p"]  





#for now ice, temp, ice_p, temp_p initialized to 0, but we can add them later when we have the data and the model for them.

ice = temp = bc = 0
ice_p = temp_p = 0


def simulate_sector_emissions (sectors:list, params: dict, time_horizon: int):
    emissions_sector = np.zeros(time_horizon)
    list_emissions = []
    for sector in sectors:
        
        GR = em.calc_growth_rate( sector, params.get(sector, 0.0), time_horizon )
        E = em.calc_sector_emissions(sector, GR, time_horizon)
        list_emissions.append({"sector": sector,"year": time_horizon, "emissions": np.round(E, 2)})
        emissions_sector += E 
    df_emissions = pd.DataFrame(list_emissions, columns=["sector", "year", "emissions"])
    df_emissions.to_csv("sector_emissions.csv", index=False)       
    return np.round(emissions_sector, 2)



def simulate_fossil_fuel_emissions( fuels:list, params: dict,  time_horizon: int):
    emissions_fossil_fuel = np.zeros(time_horizon)
    fossil_emissions = []
    for fuel in fuels:
        E = em.calc_fossil_fuel_emissions(fuel, params.get(fuel, 0.0), time_horizon)
        fossil_emissions.append({"fuel": fuel,"year": time_horizon, "emissions": np.round(E, 2)})
        emissions_fossil_fuel+= E

    df_fossil = pd.DataFrame(fossil_emissions, columns=["fuel", "year", "emissions"])
    df_fossil.to_csv("fossil_fuel_emissions.csv", index=False)    
    return emissions_fossil_fuel

def simulate_wetland_emissions( time_horizon: int):
    
    E  = em.calc_wetland_emissions( time_horizon)
    emissions_wetland =np.array(E)
    
    wetland_emissions = []
    for t in range( time_horizon ):
        wetland_emissions.append({"sector": "wetland", "year": t, "emissions": np.round(E[t-1], 2)})  
        
    df_wetland = pd.DataFrame(wetland_emissions, columns=["sector", "year", "emissions"])
    df_wetland.to_csv("wetland_emissions.csv", index=False)    
    return emissions_wetland


    

    


def simulate_combine_annual_emissions(emissions_sector: np.ndarray, emissions_fossil_fuel: np.ndarray, emissions_wetland: np.ndarray):
    combined_emissions = emissions_sector + emissions_fossil_fuel + emissions_wetland
    return combined_emissions.tolist(), np.round(np.sum(combined_emissions), 2)

def simulate_ch4_stock_update(annual_emissions: list):
    stock, stock_ppb = s.ch4_stock_update(annual_emissions)
    return stock, stock_ppb



#------------------------------   
#Delete this later, just for testing
if __name__ == "__main__":
    
    paddy = c.ch4_emission["paddy"]
    landfills = c.ch4_emission["landfills"]
    animal_ag_slider = 0.0
    coal_slider = 0.0
    oil_slider = 0.0
    gas_slider = 0.0
    land_slider = 0.0
    paddy_slider = 0.0
    shipping_slider = 0.0
    flares_slider = 0.1
    transport_slider = 0.1
    t_slider = 20

    params = {
    
        "animal_ag": animal_ag_slider,
        "coal": coal_slider,
        "oil": oil_slider,
        "gas": gas_slider,
        "landfills": land_slider,
        "paddy": paddy_slider,
        "shipping": shipping_slider,
        "flares": flares_slider,
        "transport": transport_slider
    }
    time_horizon = t_slider
    
#-------------------------------
 
#testing simulate_sector_emissions


    #sector_emission = simulate_sector_emissions(c.sector_list, params, time_horizon)  
    #print("Sector Emissions:", sector_emission)
#testing simulate_fossil_fuel_emissions
    fossil_emission = simulate_fossil_fuel_emissions(c.fossil_fuel_list, params, time_horizon)
    print("Fossil Fuel Emissions:", fossil_emission)
#testing simulate_wetland_emissions
    #wetland_emission = simulate_wetland_emissions(time_horizon)
#testing simulate_combine_annual_emissions
    #combined_emission = simulate_combine_annual_emissions(sector_emission, fossil_emission, wetland_emission)
    #print("Combined Annual Emissions:", combined_emission)
#testing simulate_ch4_stock_update
    #ch4_stock, ch4_stock_ppb = simulate_ch4_stock_update(combined_emission)
    #print("Updated CH4 Stock (Mt):", ch4_stock)
    #print("Updated CH4 Stock (ppb):", ch4_stock_ppb)    


#upto this point delete later, just for testing

#------------------------------   