# # -------------------------
# Methane emissions baseline (Global Methane Budget 2023, Saunois et al.)
# Values in Mt CH4 per year
# -------------------------

rates = {
    "oxi_r": 0.083 
}
# Card variables initialized to 0 
ice = temp = ch4 = co2 = bc = 0
co2_p = ice_p = temp_p = ch4_p = 0
base_lineCH4 = 5320

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
# -------------------------




# -------------------------
# Functions
# -------------------------

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
#CH4 Emissions
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


def  calc_shipping(t_slider, ship_slider):
    if t_slider == 0:
        return 0   
    if ship_slider == 0 : #take the growth in arctic shipping to be dafult
    #For Arctic shipping predicted growth by 2040 is 300% from 2025 -> 15 years a groth of 300%. Calculate the annual growth
        years = 15
        growth = 3
        annual_bc_growth = calculate_yearly_rate (growth,years)
        for _ in range (t_slider):
            #soot dosent get accumulated unlike CH4 or CO2,its new stock for each year
    

            bc = bc+ bc_shipping
        return bc_shipping     

            
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

# -------------------------
# Sliders
# -------------------------
season = st.toggle("Season: Winter / Summer", value=True)  # True = Summer
if season:
    bc_emission = {
    
        "shipping":0.25,
        "flare":0.20,
        "land_tran": 0.45
}
else:
    bc_emission_w = {
    
        "shipping":0.25,
        "flare":0.20,
        "land_tran": 0.65
    }

def  calc_shipping(t_slider, ship_slider):
    if t_slider == 0:
        return 0
      
    if ship_slider == 0 : #take the growth in arctic shipping to be dafult
    #For Arctic shipping predicted growth by 2040 is 300% from 2025 -> 15 years a groth of 300%. Calculate the annual growth
        years = 15
        shipping_slider = 3
        annual_bc_growth = calculate_yearly_rate (shipping_slider,years)
        for _ in range (t_slider):
            #soot dosent get accumulated unlike CH4 or CO2,itsnew stock for each year
    
            bc += bc * annual_bc_growth
            bc_shipping = bc*bc_emission["shipping"]

        return bc_shipping 

st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Time (years). </span>'
                '<span class="slider_emoji">🕰️</span>'
                '</div>', unsafe_allow_html=True)
t_slider = st.slider("", min_value=0, max_value=20, step=1, key="time")
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

col1, space, col2, col3, space, col4 = st.columns([2, 0.25, 2, 2, 0.25, 2])

to_do = ["Tundra", "Kelp Cultivation", "Peatland restoration", "Sea Ice Cover", "Cloud Brightening"]
metrics = ["co2", "ch4", "temprature", "summer"]
metrics_p = ["co2_p", "ch4_p", "temprature_p", "summer_p"]

peat_rest = 0

with col1:
    for i in range(len(to_do)):
        if to_do[i] == "Tundra":
            st.markdown('<div style="margin-bottom:-4px;">' '<span class="slider_title">Tundra Restoration (ha). </span>'
            '<span class="slider_emoji">🌱</span>'
            '</div>', unsafe_allow_html=True)
            st.markdown("<div style='margin-top: -15px;'></div>", unsafe_allow_html=True)
            tundra_slider = st.slider("", min_value=0, max_value=500_000, step=100, key="tundra", help="Area of tundra restored. Impacts CH₄ emissions and surface albedo.")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        elif to_do[i] == "Kelp Cultivation":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Kelp Cultivation (ha)</span>'
                '<span class="slider_emoji">🌿</span>'
                '</div>', unsafe_allow_html=True)
            kelp_slider = st.slider("", min_value=0, max_value=200_000, step=40, key="kelp")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        elif to_do[i] == "Sea Ice Cover":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Sea Ice Cover (Km²). </span>'
                '<span class="slider_emoji">❄️</span>'
                '</div>', unsafe_allow_html=True)
            ice_slider = st.slider("", min_value=0, max_value=4_500_000, step=850, key="sea_ice")
        elif to_do[i] == "Cloud Brightening":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Cloud Brightening </span>'
                '<span class="slider_emoji">🌨️</span>'
                '</div>', unsafe_allow_html=True)
            cloud_slider = st.slider("", min_value=0, max_value=100, step=1, key="cloud")
        elif to_do[i] == "Peatland restoration":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Peatland restoration (ha) </span>'
                '<span class="slider_emoji">🌾</span>'
                '</div>', unsafe_allow_html=True)
            peat_slider = st.slider("", min_value=0, max_value=800_000, step=150, key="peat")

emitters = ["animal_ag", "shipping", "flaring", "transport"]
black_carbon = ["shipping", "flares", "transp"]

with col4:
    for n in range(len(emitters)):
        if emitters[n] == "animal_ag":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Animal Agriculture. </span>'
                '<span class="slider_emoji">🐄</span>'
                '</div>', unsafe_allow_html=True)
            animal_ag_raw = st.slider("", min_value=-50, max_value=50, value=0, step=10, format="%d%%",key="animal_ag")
            animal_ag_slider = animal_ag_raw /100

        elif emitters[n] == "fossil_fuel":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Fossil Fuel </span>'
                '<span class="slider_emoji">⛽</span>'
                '</div>', unsafe_allow_html=True)
            fossil_slider = st.slider("", min_value=-50, max_value=50, value = 0, step=10, format="%d%%", key="fossil")
        elif emitters[n] == "land_fill":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Land Fill </span>'
                '<span class="slider_emoji">🚮</span>'
                '</div>', unsafe_allow_html=True)
            land_slider_raw = st.slider("", min_value=-50, max_value=50, value=0, format="%d%%", step = 5, key="land")
            land_slider = land_slider_raw/100
        elif emitters[n] == "paddy":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Rice Paddy cultivation </span>'
                '<span class="slider_emoji">🍚</span>'
                '</div>', unsafe_allow_html=True)
            paddy_raw = st.slider("", min_value=-50, max_value=50, step=10, value=0, format="%d%%", key="paddy")
            paddy_slider = paddy_raw/100

        elif emitters[n] == "shipping":
            st.markdown("<h5 style='color: SteelBlue; text-align: center;'>Black Carbon</h5>", unsafe_allow_html=True)
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Shipping </span>'
                '<span class="slider_emoji">🚢</span>'
                '</div>', unsafe_allow_html=True)
            shipping_slider_raw = st.slider("", min_value=-100, max_value=0, value=0, format="%d%%", step = 5, key="shipping")
            shipping_slider = shipping_slider_raw/100

# -------------------------
# Calculations
# -------------------------
tundra_rest = tundra_kelp_emission(t_slider, tundra_slider)
kelp_cult = tundra_kelp_emission(t_slider, kelp_slider)
peat_rest = peatland_restoration(t_slider, peat_slider)
cloud = 0
land_fill = 0

co2 = (tundra_rest + kelp_cult + ice + cloud + land_fill + peat_rest)
co2 = round(co2 / 1_000_000, 3)

# -------------------------
# UI Outputs
# -------------------------
with col2:
    for j in range(len(metrics)):
        if metrics[j] == "co2":
            st.markdown(f"""
<div class="card">
    <div style="text-align: center; line-height: 1.1;">
        <span style="font-size: 2.5em; font-weight: bold; color: #1e3a8a;">{co2}</span><br>
        <span style="font-size: 1em; font-weight: 400; color: #64748b;">Mt CO₂</span>
    </div>
    <div class="description">Were Added</div>
</div>
""", unsafe_allow_html=True)
        elif metrics[j] == "ch4":
            st.markdown(f"""
<div class="card">
    <div style="text-align: center; line-height: 1.1;">
        <span style="font-size: 2.5em; font-weight: bold; color: #1e3a8a;">{ch4}</span><br>
        <span style="font-size: 1em; font-weight: 400; color: #64748b;">Mt CH₄</span>
    </div>
    <div class="description">Were added</div>
</div>
""", unsafe_allow_html=True)
        elif metrics[j] == "temprature":
            st.markdown(f"""<div class="card"><h3 class="card_heading">Increase in Temperature</h3>
              <div><h3 class=variable>{temp}</h3></div></div>""", unsafe_allow_html=True)
        elif metrics[j] == "summer":
            st.markdown(f"""<div class="card"><h3 class="card_heading">Increase in Summer Sea Ice</h3>
              <div><h3 class=variable>{ice}</h3></div></div>""", unsafe_allow_html=True)

with col3:
    for k in range(len(metrics_p)):
        if metrics_p[k] == "co2_p":
            st.markdown(f"""<div class="card"><h3 class="card_heading">Mt CO₂</h3>
               <div class="description">Share of future CO₂ growth offset</div>
               <div><h3 class=variable>{co2_p}</h3></div></div>""", unsafe_allow_html=True)
        elif metrics_p[k] == "ch4_p":
            st.markdown(f"""<div class="card"><h3 class="card_heading">Mt CH₄</h3>
               <div class="description">Share of future CH₄ growth offset</div>
               <div><h3 class=variable>{ch4_p}</h3></div></div>""", unsafe_allow_html=True)
        elif metrics_p[k] == "temprature_p":
            st.markdown(f"""<div class="card"><h3 class="card_heading">Off set in Temperature rise</h3>
              <div><h3 class=variable>{temp_p}</h3></div></div>""", unsafe_allow_html=True)
        elif metrics_p[k] == "summer_p":
            st.markdown(f"""<div class="card"><h3 class="card_heading">Increase in Summer Sea Ice</h3>
              <div><h3 class=variable>{ice_p}</h3></div></div>""", unsafe_allow_html=True)

#  baseline CH4 calculation for now

global_ch4 = calc_baseCH4_release_glob(yrs=t_slider) + calc_ch4_a_ag(t_slider, animal_ag_slider)+ calc_CH4_landfill(land_slider, t_slider)+calc_paddy_emmision (paddy_slider, t_slider) + calc_fossil_fuel(t_slider,fossil_slider)
global_ch4 = round(global_ch4, 3)

#Calculating black carbon

if season:
    bc = 0.08
    shipping = bc * 0.25
    flare = bc * 0.2
    trans = bc * 0.4
    other = bc * 0.15
    
else:
    bc =  0.25
    shipping = 0
    flare = bc * 0.25
    trans = bc * 0.65
    other = bc * 0.1


bc  = shipping + flare + trans + other

#  CH4 card
st.markdown(f"""
<div class="card">
    <div style="text-align: center; line-height: 1.1;">
        <span style="font-size: 2.5em; font-weight: bold; color: #1e3a8a;">{global_ch4}</span><br>
        <span style="font-size: 1em; font-weight: 400; color: #64748b;">Mt CH₄ (atmospheric stock)</span>
    </div>
    <div class="description">With each passing year CH₄ will be added to our atmosphere by — animal agriculture, landfills, and rice paddies. This is probably the biggest deal breaker</div>
</div>
""", unsafe_allow_html=True)
# BC card
st.markdown(f"""
<div class="card">
    <div style="text-align: center; line-height: 1.1;">
        <span style="font-size: 2.5em; font-weight: bold; color: #1e3a8a;">{bc}µg/m³</span><br>
        <span style="font-size: 1em; font-weight: 400; color: #64748b;">Black Carbon AKA Soot</span>
    </div>
    <div class="description">Probably one of the most devastating impact on sea ice - black carbon absorbs solar energy and increase the temprature on the ice surface, accelariting the ice melting</div>
</div>
""", unsafe_allow_html=True)

annual_emission = ch4_enteric + ch4_landfill + ch4_paddy + ch4_fossil_fuel + ch4_wetlands