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
    #Needs source checking
    "mt_to_ppb_co2": 0.128,  # Conversion factor from Mt CO₂ to ppm in the atmosphere (approximate)
    "mt_to_ppb_ch4": 0.35,  # Conversion factor from Mt CH₄ to ppb in the atmosphere (approximate)
    "ch4_to_co2_mass": 2.5,  # Molecular weight ratio (44/16)
}
ch4_to_co2_mass = rates["ch4_to_co2_mass"] 

# Card variables initialized to 0 
ice = temp  = bc = 0
co2_p = ice_p = temp_p = ch4_p = 0
base_line = {
    "ch4": 5320,
    "co2": 41000, 
    "ch4_ppb": 1900,
    "co2_ppb": 410000
}
#ch4 = base_line["ch4"]
ch4 = 0
#co2 = base_line["co2"]
#ch4_ppb = base_line["ch4_ppb"]
#co2_ppb = base_line["co2_ppb"]



ch4_emission = {
    "animal_ag": 120,   # livestock enteric + manure
    "paddy": 40,
    "landfills": 65,       # landfills + wastewater
    "coal": 40,    
    "oil": 45,
    "gas": 35,     
    "wetlands": 180,
    "unit" : "Mt CH₄/year"   
    # "biomass_burning": 35,     # optional, could add later
}


fossil_fuel = {
    "coal": {
        1: {"years": 10, "rate": 0.2},
        2: {"years": 5, "rate": 0.05},
        3: {"years": 5, "rate": -0.01}
    },
    "oil": {
        1: {"years": 10, "rate": 0.15},
        2: {"years": 5, "rate": 0.03},
        3: {"years": 5, "rate": -0.005}

    },
    "gas": {
        1: {"years": 10, "rate": 0.25},
        2: {"years": 5, "rate": 0.1},
        3: {"years": 5, "rate": 0.0}
    }

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
    "transport": {
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

growth_rates = {
    "animal_ag": {"rate": 0.17, "years": 9},
    "landfills": {"rate": 0.5, "years": 25},
    "paddy": {"rate": 0.044, "years": 9},
}


# -------------------------
# 2. Constants
# -------------------------
# -------------------------
# Functions
# -------------------------

def calculate_yearly_rate(years, area):
    k = 0.07
    rates_list = []
    for i in range(1, years + 1):
        rate = 0.4 * math.exp(-k * i)
        rates_list.append(rate * area * -1)
    return rates_list
        


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


def calc_ch4_stock_outputs(yrs, base_line):
    # 1. Initialize everything at the top so they exist for the whole function
    #base_line here is a dict. it contains the baseline stocks and concentrations for CH4 and CO2 in the atmosphere. we use these values as the starting point for our calculations, and then we add to them based on the emissions from the different sources and the oxidation process over the years.
    stocks_ch4 = base_line["ch4"]
    ch4_ppb = base_line["ch4_ppb"]
    #stocks_ch4_ppb = base_line["ch4_ppb"]
    
    # We start with 0 new CO2 and 0 new PPB, then add to them in the loop
    co2_added = 0
    co2_ppb_added = 0 
    
    # 2.  shortcut for Year 0
    if yrs == 0:
        return stocks_ch4, co2_added, ch4_ppb, co2_ppb_added
    
    # 3.  loop for years > 0
    for _ in range(yrs):
        oxidized_ch4 = stocks_ch4 * rates["oxi_r"]
        stocks_ch4 -= oxidized_ch4
        co2_added += oxidized_ch4 * ch4_to_co2_mass
        st.write (f"Year {_+1}:oxidation={round(oxidized_ch4,2)} Mt CH₄, CO₂ added={round(co2_added,2)} Mt CO₂, Remaining CH₄ stock={round(stocks_ch4,2)} Mt CH₄")
    # 4. Final conversions
    co2_ppb = co2_added * rates["mt_to_ppb_co2"]
    ch4_ppb = stocks_ch4 * rates["mt_to_ppb_ch4"]
    
    return round(stocks_ch4, 2), round(co2_added, 2), round(ch4_ppb, 2), round(co2_ppb, 2)


def calc_annual_growth_rate(years, gowth):
    if years == 0:
        return 0
    initial = 1
    final  = 1 + gowth
    # Compute annual compounded growth rate
    
    annual_rate = pow(final / initial, 1 / years) - 1

    return annual_rate


    
def calc_fossilfuel_emissions_bau(t_slider, fossil_slider, fuel_type):
    
     #Calculate the total methane emissions from fossil fuel extraction over a specified time horizon, accounting for growth rates and oxidation.

     #Parameters:
     #- t_slider: A slider value representing the time horizon in years (0 to 20).
     #- current_emission: The current methane emission level from fossil fuel extraction.
     #- rates: A dictionary containing the oxidation rate under "oxi_r".

     #Returns:
     #- Total methane emissions from fossil fuel extraction over the specified time horizon, adjusted for oxidation.
     
    #calc_BAU_emission_fuel(t_slider, "coal") this is the function call for testing, it should return the total emissions from coal extraction over 10 years with a growth rate of 20% per year.
    #fuel =fossil_fuel[fuel_type]
    if t_slider == 0 or fossil_slider != 0:
        return 0,0,0,0
    
    # initialize the total additional emissions from fossil fuel to 0, this variable will be updated each year with the new emissions from fossil fuel extraction.
    fuel_ch4,  co2_added, ch4_ppb_fuel, co2_ppb_fuel = 0, 0, 0, 0
    current_emission = ch4_emission[fuel_type] # the current emission is the baseline emission from fossil fuel, this is the starting point for calculating the growth in emissions from fossil fuel.
    #eg. ch4_gas = ch4_emission["gas"]
    # --- PHASE 1: Years 1 to 10 ---
    phase = 1
    p1 = 10 # use 10 years as the time horizon to calculate the growth rate for phase 1.
    years_p1 = min(t_slider, p1) # calculate the number of years in phase 1 based on the time slider
    growth_rate1 = fossil_fuel[fuel_type][phase]["rate"] # get the growth rate for phase 1 from the fossil fuel data
   
    for _ in range(years_p1):
        current_emission += current_emission * growth_rate1
    # adding new emissions first - fuel ch4 will increment annually with the new emission.
        fuel_ch4 += current_emission
    # then oxidize the whole stock (new + existing)
        oxidized_ch4 = fuel_ch4 * rates["oxi_r"]
        fuel_ch4 -= oxidized_ch4
        co2_added += oxidized_ch4 * ch4_to_co2_mass
        st.write (f"Year {_+1}: stock from {fuel_type} = {round(current_emission, 2)} Mt CH₄ {round(fuel_ch4, 2)} Mt CH₄, oxidized = {round(oxidized_ch4, 2)} Mt CH₄, CO₂ added = {round(co2_added, 2)} Mt CO₂")
    if t_slider > 10:
        # --- PHASE 2: Years 11 to 15 ---
        phase = 2
        p2 = 5 # use 5 years as the time horizon to calculate the growth rate for phase 2.
        years_p2 = min(t_slider - p1, p2) # calculate the number of years in phase 2 based on the time slider
        growth_rate2 = fossil_fuel[fuel_type][phase]["rate"] # get the growth rate for phase 2 from the fossil fuel data
        for _ in range(years_p2):
            current_emission += current_emission * growth_rate2 # each year the emission increases by the growth rate for phase 2, this is the new emission for that year.
            fuel_ch4 += current_emission # the new emission is added to the total additional emissions from fossil fuel
            oxidized_ch4 = fuel_ch4 * rates["oxi_r"]
            fuel_ch4 -= oxidized_ch4 # from the total after counting for the oxidation, this is the new stocks in the atmosphere from fossil fuel emissions.
            co2_added += (oxidized_ch4) * ch4_to_co2_mass # calculate the CO2 added to the atmosphere from the oxidized CH4, using the molecular weight ratio of 2.5.
    if t_slider > 15:
        phase = 3
         # --- PHASE 3: Years 16 to 20 ---
        p3 = 5 # use 5 years as the time horizon to calculate the growth
            # rate for phase 3.
        years_p3 = min(t_slider - 15, p3) # calculate the number of years in phase 3 based on the time slider
        growth_rate3 = fossil_fuel[fuel_type][phase]["rate"] # get the growth rate for phase 3 from the fossil fuel data
        for _ in range(years_p3):
            current_emission += current_emission * growth_rate3 # each year the emission increases by the growth rate for phase 2, this is the new emission for that year.
            fuel_ch4 += current_emission # the new emission is added to the total additional emissions from fossil fuel
            oxidized_ch4 = fuel_ch4 * rates["oxi_r"] # calculate the amount of CH4 that is oxidized each year based on the oxidation rate.
            co2_added += (oxidized_ch4) * ch4_to_co2_mass # calculate the CO2 added to the atmosphere from the oxidized CH4, using the molecular weight ratio of 2.5.
            fuel_ch4 -= oxidized_ch4 # subtract the oxidized CH4 from the total CH4 to get the new total CH4 in the atmosphere after accounting for oxidation.
    
    ch4_ppb_fuel = fuel_ch4 * rates["mt_to_ppb_ch4"] # calculate the change in parts per billion (ppb) of CH4 in the atmosphere from the total additional emissions from fossil fuel, using the conversion factor from Mt CH4 to ppb. 
    co2_ppb_fuel = co2_added * rates["mt_to_ppb_co2"] # calculate the change in parts per billion (ppb) of CO2 in the atmosphere from the total CO2 added, using the conversion factor from Mt CO2 to ppm.
    st.write(f"Total CH₄ stock from {fuel_type} emissions after {t_slider} years: {round(fuel_ch4, 2)} Mt CH₄")  
    return fuel_ch4, co2_added, ch4_ppb_fuel, co2_ppb_fuel          


def calc_fossil_emission_override (fossil_slider, t_slider, fuel_type):
    
    fuel_ch4, co2_added, ch4_ppb_fuel, co2_ppb_fuel = 0, 0, 0, 0
    current_emission = ch4_emission[fuel_type] # the current emission is the baseline emission from fossil fuel, this is the starting point for calculating the growth in emissions from fossil fuel.
    
    if t_slider == 0 or fossil_slider == 0:
        return 0,0,0,0
    growth =calc_annual_growth_rate(t_slider, fossil_slider)
    
    current_emission = ch4_emission[fuel_type] # the current emission is the baseline emission from fossil fuel, this is the starting point for calculating the growth in emissions from fossil fuel.
    for _ in range(t_slider):
        current_emission += current_emission * growth # the new emission is added to the total additional emissions from fossil fuel
        fuel_ch4 += current_emission  # the new emission is added to the total additional emissions from fossil fuel
        oxidized_ch4 = fuel_ch4 * rates["oxi_r"]
        fuel_ch4 -= oxidized_ch4 # from the total after counting for the oxidation, this is the new stocks in the atmosphere from fossil fuel emissions.
        co2_added += (oxidized_ch4) * ch4_to_co2_mass # calculate the CO2 added to the atmosphere from the oxidized CH4, using the molecular weight ratio of 2.5.
        #fuel_ch4 -= oxidized_ch4
    ch4_ppb_fuel = fuel_ch4 * rates["mt_to_ppb_ch4"] # calculate the change in parts per billion (ppb) of CH4 in the atmosphere from the total additional emissions from fossil fuel, using the conversion factor from Mt CH4 to ppb.
    co2_ppb_fuel = co2_added * rates["mt_to_ppb_co2"] # calculate the change in parts per billion (ppb) of CO2 in the atmosphere from the total CO2 added, using the conversion factor from Mt CO2 to ppm.
    return fuel_ch4, co2_added, ch4_ppb_fuel, co2_ppb_fuel


def calc_sector_emission_bau (t_slider, sector_slider, sector):
    if t_slider == 0 or sector_slider != 0:
        return 0,0,0,0
    #calculate the emission rate, based on the predictions.
    # Access the global dictionary
    growth  = growth_rates[sector]["rate"]# get the growth rate for the sector from the growth rates data
    yrs = growth_rates[sector]["years"] # get the time horizon for the growth rate from the growth rates data
    annual_rate = calc_annual_growth_rate(yrs, growth) # calculate the annual growth rate based on the time horizon and the growth rate for the sector.
    
    # Initializing  accumulators
    current_emission = ch4_emission[sector] # the current emission is the baseline emission from the sector, this is the starting point for calculating the growth in emissions from the sector.
    ch4_stocks_sector, co2_added  = 0, 0
    
    for _ in range(t_slider):
        current_emission += current_emission * annual_rate # the new emission is added to the total additional emissions from fossil fuel
        st.write(f"Year {_+1}: Emission from {sector} = {round(current_emission, 2)} Mt CH₄")
        ch4_stocks_sector += current_emission # the new emission is added to the total additional emissions from the sector
        oxidized_ch4 = ch4_stocks_sector * rates["oxi_r"] # calculate the amount of CH4 that is oxidized each year based on the oxidation rate.  
        ch4_stocks_sector -= oxidized_ch4 # subtract the oxidized CH4 from the total CH4 to get the new total CH4 in the atmosphere after accounting for oxidation.
        co2_added += (oxidized_ch4) * ch4_to_co2_mass # calculate the CO2 added to the atmosphere from the oxidized CH4, using the molecular weight ratio of 2.5.
        #ch4_stocks_sector -= oxidized_ch4 
    
    co2_ppb_sector = co2_added * rates["mt_to_ppb_co2"] # calculate the change in parts per billion (ppb) of CO2 in the atmosphere from the total CO2 added, using the conversion factor from Mt CO2 to ppm.
    ch4_ppb_sector = ch4_stocks_sector * rates["mt_to_ppb_ch4"] # calculate the change in parts per billion (ppb) of CH4 in the atmosphere from the total additional emissions from the sector, using the conversion factor from Mt CH4 to ppb.
    
    return ch4_stocks_sector, co2_added, ch4_ppb_sector, co2_ppb_sector

def calc_sector_emission_override(t_slider, sector, sector_slider):
    if t_slider == 0 or sector_slider == 0:
        return 0, 0, 0, 0
    
    # Initialize variables from global data
    yrs = t_slider
    growth = sector_slider
    annual_rate = calc_annual_growth_rate(yrs, growth)
    
    # Initialize local variables
    current_emission = ch4_emission[sector] 
    ch4_stocks_sector = 0
    co2_added = 0

    for _ in range(t_slider):
        # Apply the user-defined growth/reduction rate
        current_emission *= (1 + annual_rate) 
        
        # Add yearly flow to the atmospheric stock
        ch4_stocks_sector += current_emission
        
        # Calculate oxidation on the TOTAL stock
        oxidized_this_year = ch4_stocks_sector * rates["oxi_r"]
        ch4_stocks_sector -= oxidized_this_year
        # Mass balance: convert oxidized CH4 to CO2
        co2_added += oxidized_this_year * ch4_to_co2_mass
        
        # Remove the oxidized portion from the methane stock
        #ch4_stocks_sector -= oxidized_this_year
    
    # 3. Final conversion to concentrations
    co2_ppb_sector = co2_added * rates["mt_to_ppb_co2"]
    ch4_ppb_sector = ch4_stocks_sector * rates["mt_to_ppb_ch4"]
    
    return ch4_stocks_sector, co2_added, ch4_ppb_sector, co2_ppb_sector
  


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
        "flares":0.20,
        "transp": 0.45
}
else:
    bc_emission_w = {
    
        "shipping":0.25,
        "flares":0.20,
        "transp": 0.65
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
        #annual_bc_growth = calculate_yearly_rate (growth,years)
        annual_bc_growth = calc_annual_growth_rate(years, growth) # we take the first year growth rate as the annual growth rate, this is because the growth rate is not constant over the years, it decreases as the years go by, but for simplicity we will use the first year growth rate as the annual growth rate for all years.
        for _ in range (t_slider):
            #soot dosent get accumulated unlike CH4 or CO2,its new stock for each year, but the amount of soot increases, compounding growth rate 
            bc_shipping =(bc_shipping * annual_bc_growth) +bc_shipping 
            tot_bc_shipping = tot_bc_shipping + bc_shipping
    else:
        annual_rate = calc_annual_growth_rate(t_slider, ship_slider) # we take the first year growth rate as the annual growth rate, this is because the growth rate is not constant over the years, it decreases as the years go by, but for simplicity we will use the first year growth rate as the annual growth rate for all years.

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

emitters = ["animal_ag", "shipping", "flares", "transport", "landfills", "paddy", "coal", "oil", "gas"]
black_carbon = ["shipping", "flares", "transport"]

with col4:
    for n in range(len(emitters)):
        if emitters[n] == "animal_ag":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Animal Agriculture. </span>'
                '<span class="slider_emoji">🐄</span>'
                '</div>', unsafe_allow_html=True)
            animal_ag_raw = st.slider("", min_value=-100, max_value=0, value=0, step=5, format="%d%%",key="animal_ag")
            animal_ag_slider = animal_ag_raw /100

        elif emitters[n] == "coal":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Coal </span>'
                '<span class="slider_emoji">⛽</span>'
                '</div>', unsafe_allow_html=True)
            coal_raw = st.slider("", min_value=-100, max_value=0, value = 0, step=5, format="%d%%", key="coal")
            coal_slider = coal_raw / 100
        
        elif emitters[n] == "oil":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Oil </span>'
                '<span class="slider_emoji">⛽</span>'
                '</div>', unsafe_allow_html=True)
            oil_raw = st.slider("", min_value=-100, max_value=0, value = 0, step=5, format="%d%%", key="oil")
            oil_slider = oil_raw / 100

        elif emitters[n] == "gas":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Gas </span>'
                '<span class="slider_emoji">⛽</span>'
                '</div>', unsafe_allow_html=True)
            gas_raw = st.slider("", min_value=-100, max_value=0, value = 0, step=5, format="%d%%", key="gas")
            gas_slider = gas_raw / 100

        elif emitters[n] == "landfills":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Land Fill </span>'
                '<span class="slider_emoji">🚮</span>'
                '</div>', unsafe_allow_html=True)
            land_slider_raw = st.slider("", min_value=-100, max_value=0, value=0, format="%d%%", step = 5, key="land")
            land_slider = land_slider_raw/100
        elif emitters[n] == "paddy":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Rice Paddy cultivation </span>'
                '<span class="slider_emoji">🍚</span>'
                '</div>', unsafe_allow_html=True)
            paddy_raw = st.slider("", min_value=-100, max_value=0, step=5, value=0, format="%d%%", key="paddy")
            paddy_slider = paddy_raw/100

        elif emitters[n] == "shipping":
            st.markdown("<h5 style='color: SteelBlue; text-align: center;'>Black Carbon</h5>", unsafe_allow_html=True)
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Shipping </span>'
                '<span class="slider_emoji">🚢</span>'
                '</div>', unsafe_allow_html=True)
            shipping_slider_raw = st.slider("", min_value=-100, max_value=0, value=0, format="%d%%", step = 5, key="shipping")
            shipping_slider = shipping_slider_raw/100
        elif emitters[n] == "flares":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Gas Flaring </span>'
                '<span class="slider_emoji">🔥</span>'
                '</div>', unsafe_allow_html=True)
            flares_slider_raw = st.slider("", min_value=-100, max_value=0, value=0, format="%d%%", step = 5, key="flares")
            flares_slider = flares_slider_raw/100
        elif emitters[n] == "transport":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Transport </span>'
                '<span class="slider_emoji">🚗</span>'
                '</div>', unsafe_allow_html=True)
            transport_slider_raw = st.slider("", min_value=-100, max_value=0, value=0, format="%d%%", step = 5, key="transport")
            transport_slider = transport_slider_raw/100

# ------------------------- 
# Calculations
# -------------------------

tundra_rest = tundra_kelp_emission(t_slider, tundra_slider)
kelp_cult = tundra_kelp_emission(t_slider, kelp_slider)
peat_rest = peatland_restoration(t_slider, peat_slider)
cloud = 0
landfills = 0

co2 = (tundra_rest + kelp_cult + ice + cloud + landfills + peat_rest)
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

#  baseline CH4, co2, ch4ppb, co2ppb, temp_delta calculation for now
#state 0 of the app.


#Initilizing all variables 
ch4_fuel_coal, co2_fuel_coal, ch4_ppb_coal, co2_ppb_coal = 0, 0, 0, 0
ch4_fuel_oil, co2_fuel_oil, ch4_ppb_oil, co2_ppb_oil = 0, 0, 0, 0
ch4_fuel_gas, co2_fuel_gas, ch4_ppb_gas, co2_ppb_gas = 0, 0, 0, 0
ch4_animal_ag, co2_animal_ag, ch4_ppb_animal_ag, co2_ppb_animal_ag = 0, 0, 0, 0
ch4_land_fill, co2_land_fill, ch4_ppb_land_fill, co2_ppb_land_fill = 0, 0, 0, 0
ch4_paddy, co2_paddy, ch4_ppb_paddy, co2_ppb_paddy = 0, 0, 0, 0     


if t_slider == 0:
    ch4 = base_line["ch4"]
    co2 = base_line["co2"]
    ch4_ppb = base_line["ch4_ppb"]
    co2_ppb = base_line["co2_ppb"]
    #Need to include blackcarbon for the arcitic 
    #global_temp_delta and arctic_temp_delta needs to be calcualted. 
    #global_temp_delta = 0.0
    #arctic_temp_delta = 0.0
else:
    #bau values
    ch4_coal_bau, co2_coal_bau, ch4_coal_ppb_bau, co2_coal_ppb_bau = calc_fossilfuel_emissions_bau(t_slider, coal_slider, "coal")
    #coal_list =calc_fossilfuel_emissions_bau(t_slider, coal_slider, "coal")
    ch4_oil_bau, co2_oil_bau, ch4_oil_ppb_bau, co2_oil_ppb_bau = calc_fossilfuel_emissions_bau(t_slider, oil_slider, "oil")
    ch4_gas_bau, co2_gas_bau, ch4_gas_ppb_bau, co2_gas_ppb_bau = calc_fossilfuel_emissions_bau(t_slider, gas_slider, "gas")
    ch4_animal_ag_bau, co2_animal_ag_bau, ch4_ppb_animal_ag_bau, co2_ppb_animal_ag_bau = calc_sector_emission_bau(t_slider, animal_ag_slider, "animal_ag")
    ch4_land_fill_bau, co2_land_fill_bau, ch4_ppb_land_fill_bau, co2_ppb_land_fill_bau = calc_sector_emission_bau(t_slider, land_slider, "landfills")
    ch4_paddy_bau, co2_paddy_bau, ch4_ppb_paddy_bau, co2_ppb_paddy_bau = calc_sector_emission_bau(t_slider, paddy_slider, "paddy")
    
    ch4_bau_total = ch4_coal_bau + ch4_oil_bau + ch4_gas_bau + ch4_animal_ag_bau + ch4_land_fill_bau + ch4_paddy_bau
    co2_bau_total = co2_coal_bau + co2_oil_bau + co2_gas_bau + co2_animal_ag_bau + co2_land_fill_bau + co2_paddy_bau
    ch4_bau_ppb_total = ch4_coal_ppb_bau + ch4_oil_ppb_bau + ch4_gas_ppb_bau + ch4_ppb_animal_ag_bau + ch4_ppb_land_fill_bau + ch4_ppb_paddy_bau
    co2_bau_ppb_total = co2_coal_ppb_bau + co2_oil_ppb_bau + co2_gas_ppb_bau + co2_ppb_animal_ag_bau + co2_ppb_land_fill_bau + co2_ppb_paddy_bau
    
    #override values
    ch4_coal_override, co2_coal_override, ch4_ppb_coal_override, co2_ppb_coal_override = calc_fossil_emission_override(coal_slider, t_slider, "coal")
    ch4_oil_override, co2_oil_override, ch4_ppb_oil_override, co2_ppb_oil_override = calc_fossil_emission_override(oil_slider, t_slider, "oil")
    ch4_gas_override,   co2_gas_override, ch4_ppb_gas_override, co2_ppb_gas_override = calc_fossil_emission_override(gas_slider, t_slider, "gas")
    ch4_animal_ag_override, co2_animal_ag_override, ch4_ppb_animal_ag_override, co2_ppb_animal_ag_override = calc_sector_emission_override(t_slider, "animal_ag", animal_ag_slider)
    ch4_land_fill_override, co2_land_fill_override, ch4_ppb_land_fill_override, co2_ppb_land_fill_override = calc_sector_emission_override(t_slider, "landfills", land_slider)
    ch4_paddy_override, co2_paddy_override, ch4_ppb_paddy_override, co2_ppb_paddy_override = calc_sector_emission_override(t_slider, "paddy", paddy_slider)
    
    ch4_override_total = ch4_coal_override + ch4_oil_override + ch4_gas_override + ch4_animal_ag_override + ch4_land_fill_override + ch4_paddy_override
    co2_override_total = co2_coal_override + co2_oil_override + co2_gas_override + co2_animal_ag_override + co2_land_fill_override + co2_paddy_override
    ch4_override_ppb_total = ch4_ppb_coal_override + ch4_ppb_oil_override + ch4_ppb_gas_override + ch4_ppb_animal_ag_override + ch4_ppb_land_fill_override + ch4_ppb_paddy_override
    co2_override_ppb_total = co2_ppb_coal_override + co2_ppb_oil_override + co2_ppb_gas_override + co2_ppb_animal_ag_override + co2_ppb_land_fill_override + co2_ppb_paddy_override 
    
    #baseline stocks
    ch4_baseline_stocks, co2_baseline_added, ch4_ppb_baseline, co2_ppb_baseline = calc_ch4_stock_outputs(t_slider, base_line)
    st.write(ch4_baseline_stocks)

    #Final card values
    ch4 = round(ch4_bau_total + ch4_baseline_stocks + ch4_override_total, 2)
    co2 = round(co2_bau_total + co2_baseline_added + co2_override_total, 2)
    ch4_ppb = round(ch4_bau_ppb_total + ch4_ppb_baseline + ch4_override_ppb_total, 2)
    co2_ppb = round(co2_bau_ppb_total + co2_ppb_baseline + co2_override_ppb_total, 2)

    
#Calculating black carbon


#bc  = shipping + flare + trans + other

#  CH4 card
st.markdown(f"""
<div class="card">
    <div style="text-align: center; line-height: 1.1;">
        <span style="font-size: 2.5em; font-weight: bold; color: #1e3a8a;">{ch4}</span><br>
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
