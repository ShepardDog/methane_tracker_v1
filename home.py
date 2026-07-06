# # -------------------------
# Methane emissions baseline (Global Methane Budget 2023, Saunois et al.)
# Values in Mt CH4 per year
# -------------------------
## MODEL ASSUMPTIONS
# - Time is modeled in yearly timesteps
# - Each timestep represents end-of-year state
# - year 0 is the current year and year 0 through 19 gives 20 data points and 19 years in total
# First Principle MVP version 
#this app has 2 components - emissions and interventions. Emissions are bith natural and anthropagenic
#CH4 sources and intervention is trying to tilt the balance towards reducing global temprature 


# ---------------------
# 1. Imports
# ---------------------


import streamlit as st
import constants as c
import validator as val
import emission as em
import stocks as s
import radiative as r
import co2_stocks as co
import simulation as sim
import numpy as np





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
            
    .unit { 
     
        font-size: clamp(0.75rem, 1vw, 1.2rem);
        font-weight: bold;
        color: #949292;
        
    }
            
    .slider_heading{
            
            margin-top: 24px;
            margin-bottom: 8px;
            padding-bottom: 4px;
            border-bottom: 1px solid #E0E0E0;
            font-size: 1.15rem;
            font-weight: 700;
            color: #535d63;
            
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
        color: #949292;
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

st.markdown("<h1 style='color: SteelBlue; text-align: center;'>From Methane to Melt: A 20-Year Arctic Forcing Explorer. </h1>", unsafe_allow_html=True)

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

#top section
col1, space, col2, col3, space, col4 = st.columns([2, 0.25, 2, 2, 0.25, 2])




#Emission silders
sliders_emitters = {}
sliders_bc = {}

#Sink silders
sliders_carbon_sinks = {}
sliders_CH4_sinks = {}
sliders_geo ={}
sliders_fossil={}


with col1:
    st.markdown(
        f'<div style="margin-bottom:-4px;">'
        f'<span class="slider_heading">Natural Sinks</span>'
        f'</div>', unsafe_allow_html=True
    )
    for k, v in c.carbon_sinks.items():
        title =v.get("title")
        emoji = v.get("emoji")
        st.markdown(
            f'<div style="margin-bottom:-4px;">'
            f'<span class="slider_title">{title}</span>'
            f'<span class="slider_emoji">{emoji}</span>'
            f'</div>', unsafe_allow_html=True
        )
        sliders_carbon_sinks[k] = st.slider(
            label="",
            #label_visibility="collapsed",
            min_value=v.get("min_value"),
            max_value=v.get("max_value"),
            value = v.get("value"),
            step=v.get("step"),
            key=v.get("key"),
            help=v.get("help")
            
        )
    
    st.markdown(
        f'<div style="margin-bottom:-4px;">'
        f'<span class="slider_heading">Bio Engineered Sinks</span>'
        f'</div>', unsafe_allow_html=True
    )
    for k, v in c.bio_engineered_sinks.items():
        title =v.get("title")
        emoji = v.get("emoji")
        st.markdown(
            f'<div style="margin-bottom:-4px;">'
            f'<span class="slider_title">{title}</span>'
            f'<span class="slider_emoji">{emoji}</span>'
            f'</div>', unsafe_allow_html=True
        )

        sliders_CH4_sinks[k] = st.slider(
        label="",
        min_value=v.get("min_value"),
        max_value=v.get("max_value"),
        value = v.get("value"),
        step=v.get("step"),
        key=v.get("key"),
        help=v.get("help") 
        )
        
    st.markdown(
        f'<div style="margin-bottom:-4px;">'
        f'<span class="slider_heading">Geo Engineering</span>'
        f'</div>', unsafe_allow_html=True
    )


    with st.expander("Click to Expand",expanded=False):
        for k, v in c.geo_engineered_sinks.items():
            title =v.get("title")
            emoji = v.get("emoji")
            st.markdown(
                f'<div style="margin-bottom:-4px;">'
                f'<span class="slider_title">{title}</span>'
                f'<span class="slider_emoji">{emoji}</span>'
                f'</div>', unsafe_allow_html=True

            )

            sliders_geo[k] = st.slider(
                label="",
                #label_visibility="collapsed",
                min_value=v.get("min_value"),
                max_value=v.get("max_value"),
                value = v.get("value"),
                step=v.get("step"),
                key=v.get("key"),
                help=v.get("help")
            
        )
            
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)    
            if k == "sea_ice_cover" and sliders_geo[k] > 0:
                st.warning("‼️: No long-term studies have examined whether silica bead dumping or winter brine pumping could harm pregnant and nursing seals, polar bears, their offspring, or other vulnerable Arctic species")
            
            elif k == "cloud_brightening" and sliders_geo[k] > 0:
                st.warning("⚠️: Climate models suggest that large-scale ocean cooling may alter atmospheric circulation, potentially affecting precipitation patterns, including drought risk in regions such as the Amazon")






with col4:
    st.markdown(
        f'<div style="margin-bottom:-4px;">'
        f'<span class="slider_heading">Anthropogenic Emissions</span>'
        f'</div>', unsafe_allow_html=True
    )
    for k, v  in c.emitters.items():
        title =v.get("title")
        emoji = v.get("emoji")
        st.markdown(
            f'<div style="margin-bottom:-4px;">'
            f'<span class="slider_title">{title}</span>'
            f'<span class="slider_emoji">{emoji}</span>'
            f'</div>', unsafe_allow_html=True
        )
        
        sliders_emitters[k] = st.slider(
            label="",
            #label_visibility="collapsed",
            min_value=v.get("min_value"),
            max_value=v.get("max_value"),
            value=v.get("value"),
            step=v.get("step"),
            key=v.get("key"),
            help=v.get("help")
        )
            
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)    
    

    st.markdown(
        f'<div style="margin-bottom:-4px;">'
        f'<span class="slider_heading">Fossil Fuel </span>'
        f'</div>', unsafe_allow_html=True
    

    )

    with st.expander("Click to Expand",expanded=False):
        for k, v in c.emitters_fossil.items():
        
            title =v.get("title","")
            emoji = v.get("emoji", "")
            st.markdown(
                f'<div style="margin-bottom:-4px;">'
                f'<span class="slider_title">{title}</span>'
                f'<span class="slider_emoji">{emoji}</span>'
                f'</div>', unsafe_allow_html=True

        )
        
            sliders_fossil[k] = st.slider(
                label=title,
                label_visibility="collapsed",
                min_value=v.get("min_value"),
                max_value=v.get("max_value"),
                value=v.get("value"),
                step=v.get("step"),
                key=v.get("key")
        )
            
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)    
      
    st.markdown(
        f'<div style="margin-bottom:-4px;">'
        f'<span class="slider_heading">Black Carbon</span>'
        f'</div>', unsafe_allow_html=True
        )

    with st.expander("Click to Expand",expanded=False):
        for k, v in c.black_carbon.items():
        
            title =v.get("title","")
            emoji = v.get("emoji", "")
            st.markdown(
                f'<div style="margin-bottom:-4px;">'
                f'<span class="slider_title">{title}</span>'
                f'<span class="slider_emoji">{emoji}</span>'
                f'</div>', unsafe_allow_html=True

        )
        
            sliders_bc[k] = st.slider(
                label=title,
                label_visibility="collapsed",
                min_value=v.get("min_value"),
                max_value=v.get("max_value"),
                value=v.get("value"),
                step=v.get("step"),
                key=v.get("key")
        )
            
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)    
      
    st.markdown(
        f'<div style="margin-bottom:-4px;">'
        f'<span class="slider_heading">Natural Emissions</span>'
        f'</div>', unsafe_allow_html=True
        )

    for k, v in c.natural_emissions.items():
        title =v.get("title")
        emoji = v.get("emoji")
        st.markdown(
            f'<div style="margin-bottom:-4px;">'
            f'<span class="slider_title">{title}</span>'
            f'<span class="slider_emoji">{emoji}</span>'
            f'</div>', unsafe_allow_html=True
        )
        
        sliders_emitters[k] = st.slider(
            label=title,
            label_visibility="collapsed",
            min_value=v.get("min_value"),
            max_value=v.get("max_value"),
            value=v.get("value"),
            step=v.get("step"),
            key=v.get("key"),
            disabled=True
        )

    
    
    


# -------------------------
# 2d.UI Outputs
# -------------------------


params = {
    
    "animal_ag": sliders_emitters["animal_ag"]/100,
    "coal": sliders_fossil["coal"]/100,
    "oil": sliders_fossil["oil"]/100,
    "gas": sliders_fossil["gas"]/100,
    "landfills": sliders_emitters["landfills"]/100,
    "paddy": sliders_emitters["paddy"]/100,
    "shipping": sliders_bc["shipping"]/100,
    "flares": sliders_bc["flares"]/100,
    "transport": sliders_bc["transport"]/100,
    "peat": sliders_carbon_sinks["peatland_restoration"],
    "tundra": sliders_carbon_sinks["tundra"],
    "kelp": sliders_carbon_sinks["kelp_cultivation"],
    "ice": sliders_geo["sea_ice_cover"],
    "cloud": sliders_geo["cloud_brightening"],
    "wetlands": sliders_emitters["wetlands"],
    "meth_arctic":sliders_CH4_sinks["methnotrophic_arctic"],
     "meth_tropic":sliders_CH4_sinks["methnotrophic_tropics"]
}

#main card variables initiated
#global_temp = c.global_temp
#arctic_temp = c.arctic_temp 
#sea_ice_change = c.sea_ice_change
time_horizon = t_slider
ch4_params =c.ch4parameters

sector_list = c.sector_list
fossil_fuel_list = c.fossil_fuel_list

if time_horizon == 0:
   # gross_ch4 = 0
    net_ch4 = c.ch4_baseline
    earth_warming, co2_gain, ch4_rf, ch4_added, bc_added,  = 0, 0, 0, 0, 0
    co2_sink, ch4_sink, redative_forcing, global_temp, arctic_temp, sea_ice_change = 0, 0, 0, 0, 0, 0
    
else:

    ch4_added, net_ch4, co2_gain,  redative_forcing, global_temp = sim.simulate_methane_engine(sector_list, fossil_fuel_list, params, time_horizon)
    arctic_temp = c.arctic_factor * global_temp
    #Placeholder for now - to be added in the next version
    co2_sink, ch4_sink,  sea_ice_change = 0, 0, 0, 
    
    
#-------------------------
bc_added = 0 # place holder for now - to be added in the next version
cards_emissions ={
    
    "ch4" :{"variable":ch4_added, "unit":"Tg", "description":"CH₄ Added."},
    "ch4_net":{ "variable":net_ch4,"unit":"Tg", "description":"Projected Net Atmospheric CH₄"},
    "soot":{"variable":bc_added,"unit":"µg/m³", "description":"Black Carbon AKA Soot"}
}
#-------------------------

cards_sinks ={
    
    "co2_prevented":{"variable":co2_sink, "unit":"Tg" ,"description":"Nature-Based CO₂ Removal."},
    "ch4_prevented" :{"variable":ch4_sink, "unit":"Tg" ,"description":"Nature-Based CH₄ Removal"},
    "net_rad":{"variable":redative_forcing, "unit":"W/m²" , "description":"Net Radiative Forcing."}
}

with col2:
    for k, v in c.card_baseline_co2.items():
        st.markdown(f"""
<div class="card">
    <div class="card_content">
        <span class="variable">{v.get("variable"):.2e}</span><span class="unit">{v.get("unit")}</span>
        <div class="description">{v.get("description")}</div>
    </div>
</div>
""", unsafe_allow_html=True)
    
    for k, v in cards_sinks.items():
        st.markdown(f"""
<div class="card">
    <div class="card_content">
        <span class="variable">{v.get("variable"):.2e}</span><span class="unit">{v.get("unit")}</span>
        <div class="description">{v.get("description")}</div>
    </div>
</div>
""", unsafe_allow_html=True)
        
    
       

with col3:
    
    for k, v in c.card_baseline_ch4.items():
        st.markdown(f"""
<div class="card">
    <div class="card_content">
        <span class="variable">{v.get("variable"):.2f}</span><span class="unit">{v.get("unit")}</span>
        <div class="description">{v.get("description")}</div>
    </div>
</div>
""", unsafe_allow_html=True)

    for k, v in cards_emissions.items():
        st.markdown(f"""
<div class="card">
    <div class="card_content">
        <span class="variable">{v.get("variable"):.2f}</span><span class="unit">{v.get("unit")}</span>
        <div class="description">{v.get("description")}</div>
    </div>
</div>
""", unsafe_allow_html=True)




#--------------------
# 3. Define parameters for the model to run.
#--------------------


#Bottom section
#place holder for now to test the design


card_global_temp = {
    "global_temp":{"variable":global_temp,"unit" :"⁰C","description":"𝚫 in Global Temprature"}}

card_arctic_temp ={
    "arctic_temp":{"variable":arctic_temp, "unit" :"⁰C", "description":"𝚫 in Arctic Temprature"},

}
card_sea_ice ={
     "sea_ice":{"variable":sea_ice_change, "unit": "Km²", "description":"𝚫 Sea Ice Extent"}

} 

col_global_temp, col_arctic_temp, col_sea_ice = st.columns([1,1,1])

with col_global_temp:
    for k, v in card_global_temp.items():
        st.markdown(f"""
<div class="card_main">
    <div class="card_content">
        <span class="variable">{v.get("variable"):.2f}</span><span class="unit">{v.get("unit")}</span>
        <div class="description">{v.get("description")}</div>
    </div>
</div>
""", unsafe_allow_html=True)

with col_arctic_temp:
    for k, v in card_arctic_temp.items():
        st.markdown(f"""
<div class="card_main">
    <div class="card_content">
        <span class="variable">{v.get("variable"):.2f}</span><span class="unit">{v.get("unit")}</span>
        <div class="description">{v.get("description")}</div>
    </div>
</div>
""", unsafe_allow_html=True)

with col_sea_ice:
    for k, v in card_sea_ice.items():
        st.markdown(f"""
<div class="card_main">
    <div class="card_content">
        <span class="variable">{v.get("variable"):.2f}</span><span class="unit">{v.get("unit")}</span>
        <div class="description">{v.get("description")}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write(co2_gain)






