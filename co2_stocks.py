import constants as c
import emission as em
import stocks as s
import numpy as np
import pandas as pd 



multi_factor = c.co2parameters.ch4_to_co2_mass

def co2_from_ch4(oxidation_loss, multi_factor):
    oxidation_loss = np.array(oxidation_loss)
    co2_gain = oxidation_loss * multi_factor
    return co2_gain