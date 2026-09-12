#!/usr/bin/env python3
#baseline values for storm intensity
import numpy as np
import constants as c
import random
from dataclasses import dataclass
#for testing purposes, we can set a seed for reproducibility. In production, we can use a random seed.
rng = np.random.default_rng(seed=42)
#rng = np.random.default_rng(seed=None)



#--------------------------------------------------------------------------------------
# Kelp growth year runs February–January.
# Storm data are stored in calendar order (January–December).
# A one-month modular index shift aligns the storm data with the kelp growth cycle.
#Also storm model is used inside kelp growth model as growth is determined not just by logistic formula but also by how much damage storm causes 
#---------------------------------------------------------------------------------------
p0 = c.p0
p1 = c.p1
p2 = c.p2
p3 = c.p3

#storm_strength = np.arange(1,4)


storm_strength = np.arange(1,4)
strom_prob = c.storm_prob
#--------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
def storm_starter (year, rng):
    
    #This for loop creates number of storms for that year 
    if p0.years > year:
            #create a number between storm baseline values
        
        storm_rate = (p0.storm_min_baseline+p0.storm_max_baseline)/2
        #storms = np.random.poisson(storm_rate)
        storms = rng.poisson(storm_rate)

    elif p1.years > year:
        storm_rate = (p1.storm_min_baseline+p1.storm_max_baseline)/2
        storms = rng.poisson(storm_rate)
            
    elif p2.years > year:
        storm_rate = (p2.storm_min_baseline+p2.storm_max_baseline)/2
        storms = rng.poisson(storm_rate)
            
    else :
        storm_rate = (p3.storm_min_baseline+p3.storm_max_baseline)/2
        storms = rng.poisson(storm_rate)
            
    return storms


def distribute_annual_storms (num_storms:int, rng):

    monthly_storm_frequency = {m: 0 for m in range (1, 13) } #create a slot for each month of the year 
    #for storm in range (num_storms):
    lookup_month =1 # 1 = January
    total = 0
    
    
   # initilizing the index of the dict storm_prob
    while total < num_storms:
        prob_1 = c.storm_prob[lookup_month] 
        num = rng.choice([1, 0], p= [prob_1, 1- prob_1]).item() 
        if num == 1:
            monthly_storm_frequency[lookup_month]+=1
            total+= 1

    
        lookup_month = (lookup_month%12) + 1
        
                
    return monthly_storm_frequency  

def storm_strength_simulator(storm_dict, year, rng):
   # rng = np.random.default_rng()
    strengths = [1, 2, 3]

    if year < p0.years:
        strength_prob = p0.strength_prob
    elif year < p1.years:
        strength_prob = p1.strength_prob
    elif year < p2.years:
        strength_prob = p2.strength_prob
    elif year <p3.years:
        strength_prob = p3.strength_prob

    else:
        raise ValueError(f"No storm-strength probabilities defined for year {year}")

    storm_strengths = {}

    for month, storm_count in storm_dict.items():
        storm_strengths[month] = [
            int(rng.choice(strengths, p=strength_prob))
            for _ in range(storm_count)
        ]

    return storm_strengths

                
    






    


    
        

def annual_storm_simulator(year, rng):
    #if seed is not None:
    #rng = np.random.default_rng(seed=seed)
    storms = storm_starter(year, rng)
    storm_dict = distribute_annual_storms (storms, rng)
    storm_strength= storm_strength_simulator(storm_dict,year, rng)
    return storm_strength

if __name__ == "__main__":
    year = 1
    rng = np.random.default_rng(seed=42)
    #storm_dict = {1: 2, 2: 1, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0, 8: 0, 9: 1, 10: 0, 11: 1, 12: 0}
    #s  = storm_strength_simulator(storm_dict, year)
    #print (s)
    storm_strength = annual_storm_simulator(1, rng)

    print (storm_strength)
    print (storm_strength[3])
    

    

    