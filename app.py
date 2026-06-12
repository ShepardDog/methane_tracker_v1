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
import textwrap
import emission as em
import simulation as sim
import constants as c
import stocks as s
import radiative as r



#--------------------------
# 2. Streamlit UI
# -------------------------

st.set_page_config(layout="wide")
st.markdown("""
    <style>

    /* Global layout  */
    .block-container { 
        padding-top: 1rem !important; 
        background-color:  #FAF9F6;
    }

    div[data-testid="stMarkdownContainer"] { 
        margin-bottom: 0 !important; 
        padding-bottom: 0 !important; 
    }

    div[data-testid="stSlider"] { 
        margin-top: 0 !important; 
        padding-top: 0 !important; 
        color: #1e3a8a;
    }

    /* Slider labels */
    .slider_title { 
        color:#708090; 
        font-weight:500; 
        font-size: clamp(0.9rem, 1vw, 1.2rem); 
        line-height:1.1; 
        display:inline-block; 
        margin:0; 
    }

    .slider_emoji { 
        font-size: clamp(1.2rem, 2vw, 1.8rem); 
        line-height:1; 
        display:inline-block; 
        vertical-align:middle; 
        margin-left:6px; 
    }

    /* Responsive card container */
    .card { 
        background-color: #E7E7E7; 
        padding: 1.2rem; 
        border-radius: 20px; 
        text-align: center; 
        min-height: 220px;        /* responsive instead of fixed height */
        display: flex; 
        flex-direction: column; 
        justify-content: center;  /* vertically centers content */
    }

    .card_heading { 
        margin-bottom: 4px; 
        font-size: clamp(1rem, 1.2vw, 1.6rem);
    }

    /* Metric numbers (CH₄, CO₂, etc.) added */
    .variable { 
        font-size: clamp(1rem, 4vw, 2.4rem);  /* responsive scaling */
        font-weight: bold; 
        color: #b85b61;
        text-align: center;
        margin-top: 10px; 
        white-space: nowrap;                 /* prevents wrapping */
        min-width: 0;                        /* allows shrinking */
    }
            

     /* Metric numbers (CH₄, CO₂, etc.) added */
    .variable_offset{ 
        font-size: clamp(1rem, 4vw, 2.4rem);  /* responsive scaling */
        font-weight: bold; 
        color: #6D8196;
        text-align: center;
        margin-top: 10px; 
        white-space: nowrap;                 /* prevents wrapping */
        min-width: 0;                        /* allows shrinking */
    }       

    /* Card descriptions */
    .description { 
        font-size: clamp(0.75rem, 1.75vw, 1rem); 
        font-weight: bold; 
        color: #36454F;
        margin-top: 0; 
    }

    /* Main dark card */
    .card_main { 
        background-color: #071B34; 
        padding: 1.2rem; 
        border-radius: 20px; 
        text-align: center; 
        min-height: 220px; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
    }

    .description_main_card { 
        font-size: clamp(0.75rem, 1vw, 1rem); 
        color:#EAF2FF; 
        margin-top: 0; 
    }

</style>

""", unsafe_allow_html=True)

# -------------------------
# 2a. Title
#------------------------------

st.markdown("<h1 style='color: SteelBlue; text-align: center;'>How Peat, Kelp, and 20 Years Can Buy Us Time: A Carbon Model for the Arctic</h1>", unsafe_allow_html=True)

#-----------------------------
# 2b. Subtitle
#------------------------------

st.markdown("""
    <p style='color: Navy; text-align: center; font-size: 20px;'>
    Explore potential Arctic futures under different emissions and intervention scenarios. Compare Business-as-Usual and Strong Mitigation pathways and their possible impacts on warming, sea ice, and ecosystems..
    </p>
""", unsafe_allow_html=True)

# -------------------------
# 2c.Sliders
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



st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Time (years). </span>'
                '<span class="slider_emoji">🕰️</span>'
                '</div>', unsafe_allow_html=True)
t_slider = st.slider("", min_value=0, max_value=20, step=1, key="time")
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

col1, space, col2, col3, space, col4 = st.columns([2, 0.25, 2, 2, 0.25, 2])

to_do = ["Tundra", "Kelp Cultivation", "Peatland restoration", "Sea Ice Cover", "Cloud Brightening"]
metrics = ["co2", "ch4", "ch4_stock", "soot"]
metrics_p = ["co2_p", "ch4_p", "temprature_p", "summer_p"]

peat_rest = 0

with col1:
    for i in range(len(to_do)):
        if to_do[i] == "Tundra":
            st.markdown('<div style="margin-bottom:-4px;">' '<span class="slider_title" >Tundra Restoration (ha) </span>'
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

emitters = ["animal_ag",  "landfills", "paddy", "coal", "oil", "gas", "shipping", "flares", "transport"]
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
                '<span class="slider_emoji">🪨☁</span>'
                '</div>', unsafe_allow_html=True)
            coal_raw = st.slider("", min_value=-100, max_value=0, value = 0, step=5, format="%d%%", key="coal")
            coal_slider = coal_raw / 100
        
        elif emitters[n] == "oil":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Pertolium Oil </span>'
                '<span class="slider_emoji">⛽</span>'
                '</div>', unsafe_allow_html=True)
            oil_raw = st.slider("", min_value=-100, max_value=0, value = 0, step=5, format="%d%%", key="oil")
            oil_slider = oil_raw / 100

        elif emitters[n] == "gas":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Natural Gas </span>'
                '<span class="slider_emoji">♨️</span>'
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
                '<span class="slider_emoji">🔥 🏭</span>'
                '</div>', unsafe_allow_html=True)
            flares_slider_raw = st.slider("", min_value=-100, max_value=0, value=0, format="%d%%", step = 5, key="flares")
            flares_slider = flares_slider_raw/100
        elif emitters[n] == "transport":
            st.markdown('<div style="margin-bottom:-6px;">' 
                '<span class="slider_title">Transport </span>'
                '<span class="slider_emoji">🚗💨</span>'
                '</div>', unsafe_allow_html=True)
            transport_slider_raw = st.slider("", min_value=-100, max_value=0, value=0, format="%d%%", step = 5, key="transport")
            transport_slider = transport_slider_raw/100


# -------------------------
# 2d.UI Outputs
# -------------------------

params = {
    
    "animal_ag": animal_ag_slider,
    "coal": coal_slider,
    "oil": oil_slider,
    "gas": gas_slider,
    "landfills": land_slider,
    "paddy": paddy_slider,
    "shipping": shipping_slider,
    "flares": flares_slider,
    "transport": transport_slider,
    "peat": peat_slider,
    "tundra": tundra_slider,
    "kelp": kelp_slider,
    "ice": ice_slider,
    "cloud": cloud_slider,
    "wetlands": c.ch4_emission["wetlands"]

}
time_horizon = t_slider
sector_emission = sim.simulate_sector_emissions (c.sector_list, params, time_horizon)
fuel_emission = sim.simulate_fossil_fuel_emissions( c.fossil_fuel_list, params,  time_horizon)
wetland_emission = sim.simulate_wetland_emissions( time_horizon)
#ch4_emission_lists, sim.new_ch4 = sim.simulate_combine_annual_emissions(sector_emission, fuel_emission, wetland_emission)
ch4_emission_lists, sim.new_ch4 = sim.simulate_combine_annual_emissions(
    sector_emission,
    fuel_emission,
    wetland_emission
)
st.write("combined list:", ch4_emission_lists)
st.write("new_ch4 total:", sim.new_ch4)

ch4, oxi_loss, s_update, ch4_ppb_update = sim.simulate_ch4_stock_update(ch4_emission_lists, c.ch4parameters())
ch4 = round(ch4, 2)
st.write(s_update)
st.write (ch4_ppb_update)
rf_ch4 = sim.simulate_radiative_force_methane(ch4_ppb_update, r.M0, r.RF_CONSTANT, r.N20_PPB_PROJECTION, r.H2O_SCALE)
st.write(rf_ch4)

with col2:
    for j in range(len(metrics)):
        if metrics[j] == "co2":
            st.markdown(f"""
<div class="card">
    <div class="card_content">
        <span class="variable">{sim.new_co2}</span>
        <div class="description">Tg CO₂ added.</div>
    </div>
</div>
""", unsafe_allow_html=True)
        elif metrics[j] == "ch4":
            st.markdown(f"""
<div class="card">
    <div class="card_content">
        <span class="variable">{sim.new_ch4}</span>
        <div class="description">Tg CH₄ added.</div>
    </div>
</div>
""", unsafe_allow_html=True)
        elif metrics[j] == "ch4_stock":
            st.markdown(f"""
                        <div class="card">
    <div class="card_content">
        <span class="variable">{ch4}</span>
        <div class="description">Tg CH₄ (atmospheric stock)</div>
    </div>
</div>
              """, unsafe_allow_html=True)
        elif metrics[j] == "soot":
            st.markdown(f"""
                        <div class="card">
    <div class="card_content">
        <span class="variable">{sim.bc}</span>
        <div class="description">µg/m³ Black Carbon AKA Soot</div>
    </div>
</div>
              """, unsafe_allow_html=True)

with col3:
    for k in range(len(metrics_p)):
        if metrics_p[k] == "co2_p":
            st.markdown(f"""
    <div class="card">
        <div class="card_content">
            <span class="variable_offset">{sim.co2_p}</span>
            <div class="description">Mg CO₂ growth offset</div>
        </div>
    </div>
               """, unsafe_allow_html=True)
        elif metrics_p[k] == "ch4_p":
            st.markdown(f"""
                        <div class="card">
        <div class="card_content">
            <span class="variable_offset">{sim.ch4_p}</span>
            <div class="description">Mg CH₄ growth offset</div>
        </div>
    </div>
               """, unsafe_allow_html=True)
        elif metrics_p[k] == "temprature_p":
            st.markdown(f"""
                        <div class="card">
        <div class="card_content">
            <span class="variable_offset">{sim.temp_p}</span>
            <div class="description">Temperature rise offset (°C)</div>
        </div>
    </div>
              """, unsafe_allow_html=True)
        elif metrics_p[k] == "summer_p":
            st.markdown(f"""
                        <div class="card">
        <div class="card_content">
            <span class="variable_offset">{sim.ice_p}</span>
            <div class="description">Summer Sea Ice Melt offset</div>
        </div>
    </div>
              """, unsafe_allow_html=True)


#--------------------
# 3. Define parameters for the model to run.
#--------------------







#Temperature card
st.markdown(f"""
<div class="card_main">
    <div style="text-align: center; line-height: 1.1;">
        <span style="font-size: 2.5em; font-weight: bold; color: #1e3a8a;">{sim.temp}</span><br>
        <span style="font-size: 1em; font-weight: 400; color: #64748b;">Global Temperature Rise (°C)</span>
    </div>
    <div class="description_main_card">Net deviation in Arctic atmospheric temperature resulting from the active scenario inputs.</div>
</div>
""", unsafe_allow_html=True)
# Sea Ice card


st.markdown(f"""
<div class="card_main">
    <div style="text-align: center; line-height: 1.1;">
        <span style="font-size: 2.5em; font-weight: bold; color: #1e3a8a;">{sim.ice}</span><br>
        <span style="font-size: 1em; font-weight: 400; color: #64748b;">Summer Sea Ice Melt</span>
    </div>
    <div class="description_main_card">Black carbon (soot) darkens ice surfaces, increasing heat absorption and accelerating Arctic sea ice melt.</div>
</div>
""", unsafe_allow_html=True)




