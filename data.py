import numpy as np
import pandas as pd

def combined_emissions(combined_list:list):
    df_emissions = pd.DataFrame(combined_list, columns=["sector", "year", "emissions"])
    df_emissions.to_csv("combined_emissions.csv", index=False)

def ch4_stock_annual_values(Ch4_stock_update):
    df_ch4_stocks = pd.DataFrame(Ch4_stock_update, columns=["ch4stocks", "year"])
    df_ch4_stocks.to_csv("CH4_stocks")