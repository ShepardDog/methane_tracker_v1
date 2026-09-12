import numpy as np
from dataclasses import dataclass
import constants as c
import storm as stm




#--------------------------------------------------------------------------------------    
#This model assumes one new kelp cohort is cultivated each year in an adjacent plot of equal area. All plots are assumed to experience identical environmental conditions and therefore share the same carrying capacity, initial biomass, and monthly growth rates.

#The biomass matrix represents age-specific growth trajectories, rather than individual physical cohorts.

#Row 0 corresponds to the first year of growth of any cohort
#Row 1 corresponds to the second year of growth.
#Row 2 corresponds to the third year of growth.

#Because each newly planted cohort follows the same deterministic growth assumptions, the trajectories are reusable across cohorts.

#Total standing biomass at any calendar year is obtained by summing the biomass of all active cohort ages.#


#------------------------------------------------------------------------------------------
kelp_params = c.KELP_PARAMETERS
canopy_limit = kelp_params.max_density_per_ha
r = kelp_params.kelp_growth_rates
M0 = kelp_params.initial_weight
dry_weight_factor = kelp_params.dry_weight_fraction
carbon_fraction = kelp_params.carbon_fraction
CO2_weight = kelp_params.CO2_weight





def write_kelp_matrix(time_horizon:int , months=12):
    """ this function will create a 2D array of  rows (time_horizon), 12 columns (months), and in the next function the arry will be populated by the kelp biomass
        time_horizon : user inputted int - total time period of kelp growth
        months= 12 - each column in the matrix represents months of the year , while rows represt the total numebr of years
    """

    return np.zeros((time_horizon, months))

def calc_cohort_size( ha, time_horizon):
    #1 ha  = 100m x 100m 
    #Assumption 1: longlines are setup 5m apart form each other making 20 x100m of lonlines to cover an area of 1ha 
    #Assumption2: Initial kelp biomass is set to 5 kg ha⁻¹ (0.005 Mg ha⁻¹) as a conservative model-initialization proxy, informed by a Baltic Sea Saccharina latissima farm model that assumed approximately 6 g wet biomass per metre of longline. 
    if time_horizon == 0 or ha == 0:
        return 0, 0
    annual_ha = ha/time_horizon
    mass_per_ha = kelp_params.initial_weight
    cohort_size = annual_ha * mass_per_ha
    return annual_ha, cohort_size

def calc_canopy_limit ( annual_ha,  max_density = kelp_params.max_density_per_ha):
    #Assumption 1 the canopy limit does not changes with cohorts 
    
    return max_density* annual_ha

# Kelp growth year runs February–January.
# Storm data are stored in calendar order (January–December).
# A one-month modular airthmatic aligns the storm data with the kelp growth cycle.





def calc_kelp_biomass(time_horizon: int, cohort_size: float, canopy_limit: float, r: np.array, months=12):
    """
    Simulates the monthly biomass accumulation of kelp cohorts over an extended 
    time horizon, factoring in age-specific storm vulnerabilities and logistic 
    carrying capacity limits for a wild ocean carbon forest.
    """
    rng = np.random.default_rng(seed=42)
#Seed=None will introduce real randomness 
#rng = np.random.default_rng(seed=None)
    # Initialize the 2D grid matrix (Rows = Age Years, Columns = Growth Months)
    biomass_array = write_kelp_matrix(time_horizon, months=12)
    
    # 1. Map calendar months in kelp growth order (Feb is Key 2, Jan is Key 1)
    kelp_calendar_order = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1]
    
    # Run the simulation year-by-year through the age cohorts
    for t in range(time_horizon):
        
        # Pull the calendar storm event lists for this year index
        storm_strength = stm.annual_storm_simulator(t, rng)  # Use a fixed seed for reproducibility
        
        
        # 2. Select the correct age vulnerability profile based on Row 't'
        if t == 0:
            # young kelp
            impact_map = {1: c.IMPACT1.new, 2: c.IMPACT2.new, 3: c.IMPACT3.new}
        elif t == 1:
            # medium kep growth
            impact_map = {1: c.IMPACT1.medium, 2: c.IMPACT2.medium, 3: c.IMPACT3.medium}
        else:
            # mature growth (Locks in for all subsequent years)
            impact_map = {1: c.IMPACT1.mature, 2: c.IMPACT2.mature, 3: c.IMPACT3.mature}
            
        # 3. this has a 12-month storm multipliers, align with Feb->Jan cycle
        multipliers_list = []
        for m in kelp_calendar_order:
            # 
            storms_in_month = storm_strength.get(m, [])
            
            # somemonths there can be more than 1 storm
            month_multiplier = 1.0
            for storm_level in storms_in_month:
                month_multiplier *= impact_map[storm_level]
            multipliers_list.append(month_multiplier)
            
        # Convert  NumPy array for the year
        year_storm_multipliers = np.array(multipliers_list)
        
        # --- logistic growth---
        for u in range(months):
            rt = r[u]  
            
            # SCENARIO A:  (Year 0, February) kelp just planted
            if t == 0 and u == 0:
                biomass_array[t, u] = cohort_size
                # No storm damage applied here:  nursery is protected.
                
            # SCENARIO B: (Carrying over from previous year's January)
            elif u == 0:
                M0 = biomass_array[t-1, -1]  # Get last month (Jan) of previous row
                growth_factor = np.e**rt
        
                biomass_array[t, u] = (canopy_limit * M0 * growth_factor) / (canopy_limit + M0 * (growth_factor - 1))
               
                biomass_array[t, u] *= year_storm_multipliers[u]
                
                # since M0 cna not be 0 we assume that if some storm completly wiped out all the kelp someone will replant at leat ||||l
                biomass_array[t, u] = max(biomass_array[t, u], 0.00001)
                
            
            else:
                M0 = biomass_array[t, u-1]  
                growth_factor = np.e**rt
                biomass_array[t, u] = (canopy_limit * M0 * growth_factor) / (canopy_limit + M0 * (growth_factor - 1))  
                biomass_array[t, u] *= year_storm_multipliers[u]
                biomass_array[t, u] = max(biomass_array[t, u], 0.00001)
                
    return biomass_array



def calc_carbon_mass (biomass:np.ndarray, dry_weight_factor, carbon_fraction):
# becasue the biomass was calculated using the logistic growth equation the end of the row value 
#represents the annual growth for the years - aslo in the model each cohort is represented as a row  
# the vlaue is in Tg 
    wet_mass = biomass[:,-1]
    dry_mass = wet_mass* dry_weight_factor
    annual_carbon = dry_mass* carbon_fraction
    tot_carbon = sum(annual_carbon)
    cumsum_carbon = np.cumsum(annual_carbon)
    return cumsum_carbon, tot_carbon  #Tg




def calc_CO2_sink(tot_carbon, cumsum_carbon, CO2_weight):
    return tot_carbon * CO2_weight,  cumsum_carbon * CO2_weight


def calc_CO2_ppm_removed(tot_carbon ):
    #calculate the ppm of CO2 sink
    CO2_removed_ppm = tot_carbon * 1/ c.co2_params.atmospheric_conversion_factor
    return CO2_removed_ppm

#wrapper function


def kelp_growth_simulator (time_horizon, ha, kelp_params, months=12):
    if time_horizon  <= 0 or ha <= 0:
                return 0,np.array([0.0]),0
       
    annual_ha, cohort_size = calc_cohort_size(ha, time_horizon)
    write_kelp_matrix(time_horizon, months)
    canopy_limit = calc_canopy_limit ( annual_ha,  max_density = kelp_params.max_density_per_ha)
    biomass = calc_kelp_biomass (time_horizon, cohort_size, canopy_limit, r, months=12) 
    cumsum_carbon, tot_carbon = calc_carbon_mass(biomass, dry_weight_factor, carbon_fraction)
    CO2_removed_ppm = calc_CO2_ppm_removed(tot_carbon )
    tot_CO2_sink, cum_CO2_sink = calc_CO2_sink (tot_carbon, cumsum_carbon, CO2_weight)
    return tot_CO2_sink, cum_CO2_sink, CO2_removed_ppm
    



if __name__ == "__main__":
    time_horizon = 20
    months =12
    ha = 1_000_000
    
    x, y, z = kelp_growth_simulator (time_horizon, ha, kelp_params, months=12)
    print (x)
    print (y)
    print (z)