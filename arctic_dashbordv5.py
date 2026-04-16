
# # -------------------------
# Methane emissions baseline (Global Methane Budget 2023, Saunois et al.)
# Values in Mt CH4 per year
# -------------------------

# ---------------------
# 1. Imports
# -------------------------
#from hmac import trans_36
#rom itertools import accumulate
import streamlit as st
import math
import textwrap


# -------------------------
# 2. Constants
# -------------------------1

rates = {
    "oxi_r": 0.083 
}

ch4_emission = {
    "animal_agriculture": 120,   # livestock enteric + manure
    "rice_paddies": 40,
    "landfills_waste": 65,       # landfills + wastewater
    "fossil_fuels": 130,         # oil, gas, coal
    "wetlands": 180,
    "unit" : "Mt CH₄/year"   
    # "biomass_burning": 35,     # optional, could add later
}
bc_meta = {

    "shipping": {
        "label": "Shipping",
        "emoji": "🚢",
        "min": -100, "max": 0, "step": 5, "default": 0,
        "divide": 100,
        "key": "shipping"
    },
    "flares": {
        "label": "Gas Flaring",
        "emoji": "🔥",
        "min": -100, "max": 0, "step": 5, "default": 0,
        "divide": 100,
        "key": "flares"
    },
    "transp": {
        "label": "Transport",
        "emoji": "🚗",
        "min": -100, "max": 0, "step": 5, "default": 0,
        "divide": 100,
        "key": "transport"
    }
}

ch4_enteric = ch4_emission["animal_agriculture"]
ch4_landfill = ch4_emission["landfills_waste"]
ch4_paddy = ch4_emission["rice_paddies"]
ch4_fossil_fuel = ch4_emission["fossil_fuels"]
ch4_wetlands = ch4_emission["wetlands"]

# Card variables initialized to 0 
ice = temp = ch4 = co2 = bc_tot = peat_rest= 0
co2_p = ice_p = temp_p = ch4_p = 0
base_lineCH4 = 5320
bc_shipping =1500 #(1500t of black carbon is emitted globally each year, source: https://www.nature.com/articles/s41467-020-17794-3, Source ICTT)



to_do = ["Tundra", "Kelp Cultivation", "Peatland restoration", "Sea Ice Cover", "Cloud Brightening"]
metrics = ["co2", "ch4", "temprature", "summer"]
metrics_p = ["co2_p", "ch4_p", "temprature_p", "summer_p"]



# -------------------------
# 3. Functions
# -------------------------

def slider_builder(title, small, large, k_name, help_text, e_emoji="" ):
    st.markdown('<div style="margin-bottom:-4px;">' f'<span class="slider_title"><span>{title} {e_emoji}</span></span>'
    '<span class="slider_emoji">emo</span>'
    '</div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-top: -15px;'></div>", unsafe_allow_html=True)
    s_slider = st.slider("", min_value=small, max_value=large, step=100, key=k_name, help=help_text)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    return s_slider


def tundra_kelp_emission(period, area):
    if area <= 0 or period <= 0:
        return 0
    if period <= 5:
        return area * 0.4 * period * -1
    else:
        base = area * 0.4 * 5 * -1
        decay_years = period - 5
        decay_total = sum(calculate_yearly_rate(decay_years, area))
        return base + decay_total

def calculate_yearly_rate(years, area):
    k = 0.07
    rates_list = []
    for i in range(1, years + 1):
        rate = 0.4 * math.exp(-k * i)
        rates_list.append(rate * area * -1)
    return rates_list

def peatland_restoration(period, area):
    if area <= 0 or period <= 0:
        return 0
    total_benefit = 0
    for year in range(1, period + 1):
        if year <= 10:
            annual_rate = 10 + (year * 1)
        else:
            decline_years = year - 10
            annual_rate = 20 - (decline_years * 0.8)
        total_benefit += area * annual_rate * -1
    return total_benefit


#-------------------------------------------------
# 3.1. CH4 Emissions
#-------------------------------------------------

def calc_baseCH4_release_glob(yrs):
    """
    calculate total emission from landfill, paddy and animal ag
    yrs - time horizon (int) defaults to 0 
    Assumption that there will be no growth in animal ag and other emitters.
    """
    # This is the baseline component. Additional emissions from emitter changes are calculated separately and added to total atmospheric stocks. base_lineCH4 represents the existing CH4 stocks in the atmosphere for more details please refer to architecture.md 
    
    if yrs == 0:
        return base_lineCH4
    #elif yrs > 0 #and all(emmitter==0 for emmitter in emmitters ):
    total = base_lineCH4
    # total is the current atmospheic stocks of CH4
    for _ in range(yrs):
        total += annual_emission # each year annual emission is added to the existing CH4 stocks
        #total = total * (1 - rates["oxi_r"])
        total = total * (1 - rates["oxi_r"]) #from the existing stocks the oxidation is deducted 
    return round(total, 2)



def calc_emit_growth_rate(s_slider, t_slider):
    """
    Calculate the implied annual compound growth rate given a total growth
fraction over a specified number of years.

Parameters
----------
s_slider : float
    Total fractional change over the entire period.
    Example: 0.5 = +50% total growth, -0.25 = -25% total reduction.

t_slider : int
    Number of years over which the total change occurs.

Returns
-------
float
    Annual compound growth rate as a fraction.
    Example: 0.0414 ≈ +4.14% per year.

Notes
-----
This function converts a user-defined total change assumption into
a constant annual compound rate using:

 annual_rate = (1 + s_slider)^(1 / t_slider) - 1

This is not simple linear growth; it assumes compounding.
 """
    if t_slider == 0:
        return 0
    initial = 1
    final  = 1 + s_slider
    # Compute annual compounded growth rate
    
    
    annual_rate = pow(final / initial, 1 / t_slider) - 1

    return annual_rate


def calc_ch4_a_ag(t_slider, animal_ag_slider):
    """
    t_slider: number of years
    animal_ag_slider: fractional total change (e.g., +50% = 0.5)
    oxi_r: oxidation rate (fraction)
    Methane oxidation is treated as a first-order continuous decay process with lifetime τ.
    The model uses yearly timesteps with exponential decay to approximate continuous atmospheric chemistry.
    
    Returns:
        Total additional CH4 emissions from growth only (baseline handled elsewhere)
    """

    #calculate annual growth rate
    annual_rate = calc_emit_growth_rate(animal_ag_slider, t_slider)
    
    if t_slider == 0 or annual_rate == 0:
        return 0
    current_emission = ch4_emission["animal_agriculture"]
    stocks = 0
    for _ in range(t_slider):
        yearly_emission = annual_rate * current_emission
        current_emission += yearly_emission
        stocks += yearly_emission
        stocks = stocks * (1 - rates["oxi_r"])

    return stocks


def calc_CH4_landfill(land_slider, t_slider):
    annual_rate = calc_emit_growth_rate(land_slider, t_slider)
    
    if t_slider == 0 or annual_rate == 0:
        return 0
    current_emission = ch4_emission["landfills_waste"]
    stocks = 0
    for _ in range(t_slider):
        yearly_emission = annual_rate * current_emission
        current_emission += yearly_emission
        stocks += yearly_emission
        stocks = stocks * (1 - rates["oxi_r"])

    return stocks
    

def calc_paddy_emmision (paddy_slider, t_slider):
    annual_rate = calc_emit_growth_rate(paddy_slider, t_slider)
    
    if t_slider == 0 or annual_rate == 0:
        return 0
    current_emission = ch4_emission["rice_paddies"]
    stocks = 0
    for _ in range(t_slider):
        yearly_emission = annual_rate * current_emission
        current_emission += yearly_emission
        stocks += yearly_emission
        stocks = stocks * (1 - rates["oxi_r"])

    return stocks

def calc_fossil_fuel (fossil_slider, t_slider):
    annual_rate = calc_emit_growth_rate(fossil_slider, t_slider)
    
    if t_slider == 0 or annual_rate == 0:
        return 0
    current_emission = ch4_emission["fossil_fuels"]
    stocks = 0
    for _ in range(t_slider):
        yearly_emission = annual_rate * current_emission
        current_emission += yearly_emission
        stocks += yearly_emission
        stocks = stocks * (1 - rates["oxi_r"])

    return stocks


def  calc_shipping(t_slider, ship_slider, bc_shipping):
    if t_slider == 0:
        return 0  
    #initiate the tot_bc_shipping variable to accumulate the total emissions over the years. this does not mean at the end of the time period there will be tot_bc_shipping amount of black carbon in the atmosphere, as black carbon has a short atmospheric lifetime and does not accumulate like CH4 or CO2. This variable is just to show the total emissions over the years based on the growth rate.
    tot_bc_shipping = 0 
    if ship_slider == 0 : #take the growth in arctic shipping to be dafult
    #For Arctic shipping predicted growth by 2040 is 300% from 2025 -> 15 years a groth of 300%. Calculate the annual growth- compunded rate
        years = 15
        growth = 3
        annual_bc_growth = calculate_yearly_rate (growth,years)
        for _ in range (t_slider):
            #soot dosent get accumulated unlike CH4 or CO2,its new stock for each year, but the amount of soot increases, compounding growth rate 
            bc_shipping =(bc_shipping * annual_bc_growth) +bc_shipping 
            tot_bc_shipping = tot_bc_shipping + bc_shipping
    else:
        annual_rate = calc_emit_growth_rate(ship_slider, t_slider)
        for _ in range(t_slider):
            bc_shipping += annual_rate * bc_shipping
            tot_bc_shipping += bc_shipping

             
    return bc_shipping , tot_bc_shipping    

# -------------------------
# Streamlit UI Setup
# -------------------------

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    div[data-testid="stMarkdownContainer"] { margin-bottom: 0 !important; padding-bottom: 0 !important; }
    div[data-testid="stSlider"] { margin-top: 0 !important; padding-top: 0 !important; }
    .slider_title { color:#708090; font-weight:500; font-size:1.0em; line-height:1.1; display:inline-inline; margin:0; padding-bottom:0; }
    .slider_emoji { font-size:1.5em; line-height:1; display:inline-inline; vertical-align:middle; margin-left:6px; margin:0; padding-bottom:0 !important; }
    .card { background-color: #0B132B; padding: 20px; border-radius: 10px; text-align: center; }
    .card_heading { margin-bottom: 2px; }
    .variable { font-size: large; font-weight: bold; margin-top: 10px; }
    .description { font-size: 0.75em; color: purple; margin-top: 0; padding-top:0; }
    </style>
""", unsafe_allow_html=True)

 # Title
st.markdown("<h1 style='color: SteelBlue; text-align: center;'>How Peat, Kelp, and 20 Years Can Buy Us Time: A Carbon Model for the Arctic</h1>", unsafe_allow_html=True)

# Subtitle
st.markdown("""
    <p style='color: Navy; text-align: center; font-size: 20px;'>
    Explore how climate interventions can slow Arctic warming, extend summer sea ice,
    and improve survival of Arctic species.
    </p>
""", unsafe_allow_html=True)
