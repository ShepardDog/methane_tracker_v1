import streamlit as st

st.set_page_config(page_title="Scope & Limitations — PoleWatch CH₄", layout="wide")
 
st.markdown("""
<style>
            
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,600;1,300&display=swap');
body {
    background-color: #FAF9F6;
    line-height: 1.6;
}

.eyebrow {
    font-size: clamp(0.7rem, 0.8vw, 0.85rem);
    font-weight: bold;
    color: #A07820;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-family: monospace;
}

.h1_heading {
    font-size: clamp(1.8rem, 3vw, 2.8rem);
    font-weight: bold;
    color:#4682B4;
}

.h2_heading {

    font-weight: bold;
    color:#4A6B7A;
}

            
.h3_heading {

    font-weight: bold;
    color:#4A6B7A;
}

.h4_heading {

    font-weight: bold;
    color:#4A6B7A;
}
                                    
.subtitle {
    font-size: clamp(0.9rem, 1.2vw, 1.1rem);
    color: #708090;
    font-style: italic;
}

.paragraph {
    font-size: clamp(0.9rem, 1.1vw, 1rem);
    font-weight: 300;
    color: #2F3E46;
    line-height: 1.75;
    max-width: 70ch;
}
           
</style>

<div class="eyebrow">PoleWatch</div>            
<h1><div class="h1_heading">Methane to Melt (M2M) Model<div></h1>          

<p class="paragraph">A simplified atmospheric scenario modeling tool for Arctic CH₄ forcing</p>

<p class="paragraph">M2M is a part of Larger PoleWatach project , where the health of the Arctic eco system is </p>
<p>Scientific Modeling: This page documents what the model does, what it does not do, and where it is going.</P>

<h2 class="h2_heading">About V0.5 </h2>
            
 <p class="paragraph">This tool models the atmospheric impact of methane (CH₄) emissions across key sectors over a 20-year horizon.
    It chains sector-level emissions through atmospheric stock accumulation, radiative forcing, temperature anomaly,
    and estimated summer Arctic sea ice loss. It is built on published parameters from IPCC AR6 and NOAA
    observational baselines.</p>

<p class="paragraph">
    It is a simplified scenario explorer, not a predictive forecast. Outputs are directional.
    The model is designed to make the CH₄ forcing chain tangible and interactive.
</p>
            
<p class="paragraph">
    Black carbon (soot) is modeled as a parallel chain — emissions → atmospheric concentration →
    albedo reduction — but is not yet integrated into the aggregate temperature and sea ice outputs.
    This will be addressed in V0.6.
</p>
 
<!-- ── 2. Who This Is For ── -->
<h2 class="h2_heading">Who This Is For</h2>


<p class="paragraph">    This version of the model is intended for:
</p>
<h3 class="h3_heading">Science educators</h3> 
            <p>The interactive sliders make the CH₄ forcing chain
    tangible for students and general audiences. The causal sequence from sector emissions to Arctic
    sea ice loss is difficult to convey in static diagrams; this tool makes it explorable.
</p>
<h3 class="h3_heading">Conservation advocates</h3> 
<p class="paragraph">The model allows users to explore how reductions in specific emission sectors connect to Arctic outcomes over a 20-year horizon, without requiring
    technical background in atmospheric physics.</P>
</p>
<h3 class="h3_heading">Animal rights activists</h3> — 
<p class="paragraph">Arctic species — polar bears, ringed seals,
    narwhals, seabirds — depend directly on summer sea ice extent. This tool makes the link between
    human emission choices and Arctic habitat loss concrete and interactive. The intervention sliders
    also surface ethical trade-offs: some geoengineering approaches, due to lack of laong term studies are conidered as potentially harmful for vulnerable Arctic species espically pregnent or nursing species who use sea ice bed a birthing and nursing grounds. 
    the apporaches are generally considered as help  reduce warming.
</p>
<h3 class="h3_heading">Early-career researchers</h3> — 
<p class="paragraph">The model serves as a reference implementation
    of the CH₄ atmospheric forcing chain using IPCC AR6 parameters. It is not a research instrument,
    but the underlying physics and parameter choices are documented and citable.
</p>
 
<!-- ── 3. Data Sources ── -->
>
    <h2 class="h2_heading">Data Sources & Parameters<h2>

IPCC AR6 — perturbation lifetime τ = 11.8 ± 1.8 years

Radiative forcing
Myhre et al. simplified expression with CH₄–N₂O band overlap correction (AR6)
Baseline CH₄ stock
NOAA Global Monitoring Laboratory — ~1922 ppb (2024 reference anchor)
Sector emissions
Global Methane Budget 2023 (Saunders et al.) — values in Tg CH₄/year
Wetland emissions
~180 Tg CH₄/year — Global Methane Budget 2023
Sea ice sensitivity
Simplified linear relationship derived from IPCC AR6 projections
Black carbon
Sector-level emission factors — Bond et al. 2013 / IPCC AR5

 
<!-- ── 4. Limitations ── -->
<h2 class="h2_heading">Simplifications & Limitations</h2>

    The following are known simplifications in V0.5. They do not invalidate the model's
    directional outputs, but should be understood before interpreting results.

<h3 class="h3_heading">CO₂ not modeled</h3>
  
<p class="paragraph">This is a CH₄-only forcing model. CO₂ emissions are entirely excluded for thi verion (V.05)
Carbon sinks (tundra, kelp, peatland) are modeled for their CO₂ sequestration effect only —
they do not interact with the CH₄ stock or radiative forcing chain.</p>
 
<h3 class="h3_heading">Biomass burning excluded</h3>
   <p class="paragraph"> Biomass burning is a significant global CH₄ source and is not currently included.
        It may be added in a future version.</P>

 
<h3 class="h3_heading">Wetland emissions — flat constant</h3>
    
     <p class="paragraph">   Wetland emissions are held at 180 Tg/year. The user cannot adjust this value.
        In reality, warmer temperatures increase wetland extent and microbial activity,
        producing more CH₄. This temperature-driven feedback is not modeled in V-0.6.</p>

 
<h3 class="h3_heading">Peatland — CO₂ sink only</h3>
   
        <p class="paragraph">Peatland restoration is modeled as a CO₂ sink. In practice, waterlogged peatlands
        also emit CH₄ through anaerobic decomposition — restoration can increase CH₄ in the
        short term even while sequestering carbon. This dual role is not captured in V-0.5.</p>


<h3 class="h3_heading">Tundra — CO₂ sink only</h3>
 
<p class="paragraph">Tundra restoration is modeled as a CO₂ sink. The suppression of permafrost-thaw
        CH₄ emissions through tundra restoration — a critical Arctic feedback — is not
        currently modeled.</p>

 
<h3 class="h3_heading">Kelp — CO₂ sink only</h3>
 
        <p class="paragraph">Kelp cultivation is modeled as a CO₂ sink through photosynthesis and carbon export.
        Some research suggests kelp ecosystems may oxidize dissolved CH₄ in seawater,
        but this effect is not well-quantified in the literature and is not modeled here.</p>


 
<h3 class="h3_heading">Black carbon — not integrated</h3>

        <p class="paragraph">Black carbon (soot) is modeled in a parallel chain — sector emissions → atmospheric
        concentration (μg/m³) → albedo reduction. It is not yet wired into the aggregate
        temperature anomaly or sea ice loss outputs. These remain CH₄-driven only in V0.5.</P>

 
<h3 class="h3_heading">No feedback loops</h3>
  
        <p class="paragraph">The model does not capture self-reinforcing feedbacks: warming → permafrost thaw → CH₄
        release → more warming, or warming → sea ice loss → albedo reduction → more warming.
        These are among the most consequential dynamics in Arctic climate and are planned for V-1+.<-p>

<h3 class="h3_heading">N₂O — background correction only</h3>
  
        <p class="paragraph">Nitrous oxide (N₂O) is included as a hardcoded background correction in the CH₄–N₂O
        radiative forcing overlap term. It is not user-controllable and does not appear in the UI.</p>

 
<h3 class="h3_heading">No spatial resolution</h3>
   
        <p class="paragraph">All values are global means. The model does not resolve regional emissions,
        regional temperature responses, or Arctic-specific circulation dynamics.</p>

 
<!-- ── 5. Roadmap ── -->
<h2 class="h2_heading">Roadmap</h2>

 
<h3 class="h3_heading">V0.6</h3>
   
        <p class="paragraph">Integrate black carbon chain into aggregate temperature and sea ice outputs.
        Add biomass burning as a CH₄ emission source.
        Dynamic wetland emissions responding to modeled temperature anomaly.</p>

<h3 class="h3_heading">V0.7</h3>
    
       <p class="paragraph"> Close the permafrost feedback loop: modeled temperature increase drives tundra thaw CH₄ release.
        Peatland dual role — CO₂ sink and CH₄ source — modeled simultaneously.
        Plain-language output summaries for non-technical audiences.
        Separate home page with narrative framing before the tool.</P>

<h3 class="h3_heading">V0.8 - V1</h3>
 
       <p class="paragraph"> CO₂ emissions and full GHG forcing integration.</p>

<h3 class="h3_heading">V2.0+</h3>
       <p class="paragraph"> Arctic food web network analysis linked to sea ice projections.
        Integration with PoleWatch PostgreSQL database and historical sea ice baselines.
        Scenario comparison mode — side-by-side BAU vs. strong mitigation.</p>

<!-- ── 6. Contact ── -->
<h3class="h3_heading">Contact Info</h3>
    <p>Rashomi Silva — PoleWatch</p>
   
        📧 <a href="mailto:rashomi@gmail.com">rashomi@gmail.com</a>

    
        🐙 <a href="https://github.com/ShepardDog/polewatch" target="_blank">github.com/ShepardDog/polewatch</a>
  
    
        <p class="paragraph">This model is under active development. Feedback, corrections, and collaboration enquiries are welcome.</p>

""", unsafe_allow_html=True)