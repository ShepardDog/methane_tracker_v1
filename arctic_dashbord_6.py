# # -------------------------
# Methane emissions baseline (Global Methane Budget 2023, Saunois et al.)
# Values in Mt CH4 per year
# -------------------------
## MODEL ASSUMPTIONS
 # - Time is modeled in yearly timesteps
 # - Each timestep represents end-of-year state
 # - Emissions are added before oxidation within each year
 # - Methane oxidation is approximated as a constant fractional decay
 # - Source contributions are modeled independently and summed

## Methane Modeling Approach
 #- Discrete yearly timestep model
 #- End-of-year state representation
 #- Emissions added before oxidation
 #- First-order decay approximation for CH₄ oxidation

# ---------------------
# 1. Imports
# -------------------------
#from hmac import trans_36
#rom itertools import accumulate
import streamlit as st
import math
import textwrap

rates = {
    "oxi_r": 0.083,
    "ppb_ch4": 1930,
    "mt_to_ppb": 2.75,
    "ch4_to_co2_mass": 2.75,  # Molecular weight ratio (44/16)
}

# Card variables initialized to 0 
ice = temp = ch4 = co2 = bc = 0
co2_p = ice_p = temp_p = ch4_p = 0
base_lineCH4 = 5320

ch4_emission = {
    "animal_agriculture": 120,   # livestock enteric + manure
    "paddy": 40,
    "landfills": 65,       # landfills + wastewater
    "coal": 40,    
    "oil": 45,
    "gas": 35,     
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

fuel_usage_1 ={
    "coal": -0.005, 
    "oil": 0.003, 
    "gas": 0.015  
}
fuel_usage_2 ={
    "coal": -0.01, 
    "oil": 0.0, 
    "gas": 0.005  
}

fuel_usage_3 ={
    "coal": -0.01, 
    "oil": -0.005, 
    "gas": 0.0  
}

ch4_enteric = ch4_emission["animal_agriculture"]
ch4_landfill = ch4_emission["landfills_waste"]
ch4_paddy = ch4_emission["rice_paddies"]
ch4_fossil_fuel = ch4_emission["fossil_fuels"]
ch4_wetlands = ch4_emission["wetlands"]



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
    Calculate the remaining baseline CH₄ in the atmosphere after accounting for oxidation over a given number of years.
    """
    # This is the baseline component. Additional emissions from emitter changes are calculated separately and added to total atmospheric stocks. base_lineCH4 represents the existing CH4 stocks in the atmosphere for more details please refer to architecture.md 
    
    if yrs == 0:
        return base_lineCH4
    
    for _ in range(yrs):
        base_lineCH4*= (1 - rates["oxi_r"])  # from the existing stocks the oxidation is deducted
        
    return round(base_lineCH4, 2)



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

#Calculating the animal ag growth rate: preidcted growth in animal ag is 17% by 2034. This is a lower bound since the model is focusing till 2040. 
def calc_annual_growth_rate(years, gowth):
    if years == 0:
        return 0
    initial = 1
    final  = 1 + gowth
    # Compute annual compounded growth rate
    
    annual_rate = pow(final / initial, 1 / years) - 1

    return annual_rate

def calc_ch4_a_ag(t_slider, animal_ag_slider):
    """
    t_slider: number of years
    animal_ag_slider: fractional total change (e.g., -50% = -0.5)
    oxi_r: oxidation rate (fraction)
    Methane oxidation is treated as a first-order continuous decay process with lifetime τ.
    The model uses yearly timesteps with exponential decay to approximate continuous atmospheric chemistry.
    
    Returns:
        atmospheric CH₄ contribution from animal agriculture over t_slider years, with growth and oxidation applied
    """

    #calculate annual growth rate
    #annual_rate = calc_emit_growth_rate(animal_ag_slider, t_slider)
    
    if t_slider == 0: 
        return 0
    if animal_ag_slider == 0:
        yrs = 9 # use 9 years as the time horizon to calculate the growth rate since the predicted growth is for 2034 and prediction made in 2025.
        rate = 0.17 # use the predicted growth in animal ag to calculate the growth rate.
        #initialize varilbles used in the for loop.
        total = 0
        delta_ppb = 0 #for ppb calculation
        current_emission = ch4_emission["animal_agriculture"] # the current emission is the baseline emission from animal agriculture, this is the starting point for calculating the growth in emissions from animal agriculture.
        growth = calc_annual_growth_rate(yrs, rate) # use the predicted growth in animal ag to calculate the annual growth rate.
        
        for _ in range(t_slider):
            
            current_emission += current_emission* growth # each year the emission increases by the growth rate, this is the new emission for that year.
            total += current_emission # the new emission is added to the total additional emissions from animal
            total = total * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from animal ag emissions.
            delta_ppb += total/rates["ppb_ch4"]
        return total, delta_ppb
    else:
        growth = calc_emit_growth_rate(animal_ag_slider, t_slider) 
        total = 0
        delta_ppb = 0 #for ppb calculation
        current_emission = ch4_emission["animal_agriculture"] # the current emission is the baseline emission from animal agriculture, this is the starting point for calculating the growth in emissions from animal agriculture.
        #current_emission = ch4_emission["animal_agriculture"]+  ch4_emission["animal_agriculture"]* growth
        for _ in range(t_slider):
            current_emission += current_emission* growth # each year the emission increases by the growth rate, this is the new emission for that year.
            total += current_emission # the new emission is added to the total additional emissions from animal
            total = total * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from animal ag emissions.
            delta_ppb += total/rates["ppb_ch4"]
        return total, delta_ppb



def calc_CH4_landfill(land_slider, t_slider):
    if t_slider == 0: 
        return 0
    if land_slider == 0:
        yrs = 25 # use 25 years as the time horizon to calculate the growth rate since the predicted growth is for 2050 and prediction made in 2025.
        rate = 0.5 # use the predicted growth in land fill to calculate the growth rate.
        #initialize varilbles used in the for loop.
        total = 0
        current_emission = ch4_emission["landfills"] # the current emission is the baseline emission from landfills, this is the starting point for calculating the growth in emissions from landfills.
        growth = calc_annual_growth_rate(yrs, rate) # use the predicted growth in landfills to calculate the annual growth rate.
        for _ in range(t_slider):
            
            current_emission += current_emission* growth # each year the emission increases by the growth rate, this is the new emission for that year.
            total += current_emission # the new emission is added to the total additional emissions from animal
            total = total * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from animal ag emissions.
        # calculate the ppb increase in the atmosphere from the total additional emissions from landfills, this is done by multiplying the total additional emissions from landfills by the conversion factor from Mt CH4 to ppb in the atmosphere. The conversion factor is calculated by dividing the total mass of CH4 in the atmosphere (in Mt) by the total number of ppb in the atmosphere. The total mass of CH4 in the atmosphere is calculated by multiplying the baseline CH4 concentration (in ppb) by the total mass of the atmosphere (in Mt) and dividing by 1e9 to convert from ppb to fraction. The total number of ppb in the atmosphere is calculated by dividing the total mass of the atmosphere (in Mt) by the molar mass of air (in g/mol) and multiplying by Avogadro's number to get the total number of molecules in the atmosphere, then dividing by 1e9 to convert from molecules to ppb.
        
        return total
    else:
        growth = calc_emit_growth_rate(land_slider, t_slider) 
        total = 0
        current_emission = ch4_emission["landfills"] # the current emission is the baseline emission from landfills, this is the starting point for calculating the growth in emissions from landfills.
        
        for _ in range(t_slider):
            current_emission += current_emission* growth # each year the emission increases by the growth rate, this is the new emission for that year.
            total += current_emission # the new emission is added to the total additional emissions from landfills
            total = total * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from landfills emissions.

        return total

    

def calc_paddy_emmision (paddy_slider, t_slider):
    if t_slider == 0: 
        return 0
    if paddy_slider == 0:
        yrs = 9 # use 9 years as the time horizon to calculate the growth rate since the predicted growth is for 2050 and prediction made in 2025.
        rate = 0.044 # use the predicted growth in paddy fields to calculate the growth rate.
        #initialize varilbles used in the for loop.
        total = 0
        current_emission = ch4_emission["paddy"] # the current emission is the baseline emission from paddy fields, this is the starting point for calculating the growth in emissions from paddy fields.
        growth = calc_annual_growth_rate(yrs, rate) # use the predicted growth in paddy fields to calculate the annual growth rate.
        for _ in range(t_slider):
            
            current_emission += current_emission* growth # each year the emission increases by the growth rate, this is the new emission for that year.
            total += current_emission # the new emission is added to the total additional emissions from animal
            total = total * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from animal ag emissions.
        return total
    else:
        growth = calc_emit_growth_rate(paddy_slider, t_slider) 
        total = 0
        current_emission = ch4_emission["paddy"] # the current emission is the baseline emission from paddy fields, this is the starting point for calculating the growth in emissions from paddy fields.
        
        for _ in range(t_slider):
            current_emission += current_emission* growth # each year the emission increases by the growth rate, this is the new emission for that year.
            total += current_emission # the new emission is added to the total additional emissions from paddy fields
            total = total * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from paddy fields emissions.

        return total
    
def calc_fossilfuel_emissions_bau(t_slider, fuel_type):
                              
     """
     Calculate the total methane emissions from fossil fuel extraction over a specified time horizon, accounting for growth rates and oxidation.

     Parameters:
     - t_slider: A slider value representing the time horizon in years (0 to 20).
     - current_emission: The current methane emission level from fossil fuel extraction.
     - rates: A dictionary containing the oxidation rate under "oxi_r".

     Returns:
     - Total methane emissions from fossil fuel extraction over the specified time horizon, adjusted for oxidation.
     """
     if t_slider == 0:
        return 0
     annual_rate = fuel_usage_1[fuel_type] # use the predicted growth in coal usage to calculate the growth rate.
     current_emission = ch4_emission[fuel_type]
     total = 0
     for _ in range(min(t_slider,10)):
        current_emission += current_emission * annual_rate
        total += current_emission
        total = total * (1 - rates["oxi_r"])
     if t_slider <= 10:
        return total

        # Calculate for the next 5 years.
                
                
     annual_rate = fuel_usage_2[fuel_type]

     for _ in range(min(t_slider - 10, 5)):
            current_emission += current_emission * annual_rate
            total += current_emission
            total = total * (1 - rates["oxi_r"])
     if t_slider <= 15:
        return total
          
        # Calculate for the last few years.
     annual_rate = fuel_usage_3[fuel_type] # use the predicted growth in coal usage to calculate the growth rate.
       
     for _ in range(t_slider - 15):
        current_emission += current_emission * annual_rate
        total += current_emission
        total = total * (1 - rates["oxi_r"])

     return total  

def calc_fossilfuel_emission_override (fossil_slider, t_slider, fossil_type):
    if t_slider == 0:
        return 0
    growth = calc_emit_growth_rate(fossil_slider, t_slider) 
    total = 0
    current_emission = ch4_emission[fossil_type] # the current emission is the baseline emission from fossil fuel, this is the starting point for calculating the growth in emissions from fossil fuel.
        
    for _ in range(t_slider):
        current_emission += current_emission* growth # each year the emission increases by the growth rate, this is the new emission for that year.
        total += current_emission # the new emission is added to the total additional emissions from coal
        total = total * (1 - rates["oxi_r"]) # from the total after counting for the oxidation, this is the new stocks in the atmosphere from coal emissions.

    return total  

def calc_coal_emission (coal_slider, t_slider):
    
    if t_slider == 0:
        return 0
    if coal_slider == 0:
        return calc_fossilfuel_emissions_bau(t_slider, "coal")
        
    return calc_fossilfuel_emission_override(coal_slider, t_slider, "coal")
    

def calc_oil_emission (oil_slider, t_slider):
    
    if t_slider == 0:
        return 0
    if oil_slider == 0:
        return calc_fossilfuel_emissions_bau(t_slider, "oil")
        
    return calc_fossilfuel_emission_override(oil_slider, t_slider, "oil")

def calc_gas_emission (gas_slider, t_slider):
    
    if t_slider == 0:
        return 0
    if gas_slider == 0:
        return calc_fossilfuel_emissions_bau(t_slider, "gas")
        
    return calc_fossilfuel_emission_override(gas_slider, t_slider, "gas")
    
def fossil_fuel_emission (coal_slider, oil_slider, gas_slider, t_slider):
    if t_slider == 0:
        return 0
    coal_emission = calc_coal_emission(coal_slider, t_slider)
    oil_emission = calc_oil_emission(oil_slider, t_slider)
    gas_emission = calc_gas_emission(gas_slider, t_slider)
    return coal_emission + oil_emission + gas_emission             
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

emitters = ["animal_ag", "shipping", "flaring", "transport", "land_fill", "paddy", "coal", "oil", "gas"]
black_carbon = ["shipping", "flares", "transp"]

with col4:
    for n in range(len(emitters)):
        if emitters[n] == "animal_ag":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Animal Agriculture. </span>'
                '<span class="slider_emoji">🐄</span>'
                '</div>', unsafe_allow_html=True)
            animal_ag_raw = st.slider("", min_value=-100, max_value=0, value=0, step=-5, format="%d%%",key="animal_ag")
            animal_ag_slider = animal_ag_raw /100

        elif emitters[n] == "coal":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Coal </span>'
                '<span class="slider_emoji">⛽</span>'
                '</div>', unsafe_allow_html=True)
            coal_raw = st.slider("", min_value=-100, max_value=0, value = 0, step=-5, format="%d%%", key="coal")
            coal = coal_raw / 100
        
        elif emitters[n] == "oil":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Oil </span>'
                '<span class="slider_emoji">⛽</span>'
                '</div>', unsafe_allow_html=True)
            oil_raw = st.slider("", min_value=-100, max_value=0, value = 0, step=-5, format="%d%%", key="oil")
            oil = oil_raw / 100

        elif emitters[n] == "gas":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Gas </span>'
                '<span class="slider_emoji">⛽</span>'
                '</div>', unsafe_allow_html=True)
            gas_raw = st.slider("", min_value=-100, max_value=0, value = 0, step=-5, format="%d%%", key="gas")
            gas = gas_raw / 100

        elif emitters[n] == "land_fill":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Land Fill </span>'
                '<span class="slider_emoji">🚮</span>'
                '</div>', unsafe_allow_html=True)
            land_slider_raw = st.slider("", min_value=-100, max_value=0, value=0, format="%d%%", step = -5, key="land")
            land_slider = land_slider_raw/100
        elif emitters[n] == "paddy":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Rice Paddy cultivation </span>'
                '<span class="slider_emoji">🍚</span>'
                '</div>', unsafe_allow_html=True)
            paddy_raw = st.slider("", min_value=-100, max_value=0, step=-5, value=0, format="%d%%", key="paddy")
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

""" if season:
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
        other = bc * 0.1 """


#bc  = shipping + flare + trans + other

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

#annual_emission = ch4_enteric + ch4_landfill + ch4_paddy + ch4_fossil_fuel + ch4_wetlands