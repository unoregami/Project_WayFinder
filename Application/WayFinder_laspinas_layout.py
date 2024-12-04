import folium
import streamlit as st
from streamlit_folium import st_folium
import requests

geojsondata = r"https://raw.githubusercontent.com/unoregami/Project_WayFinder/refs/heads/main/pasay.json"   # From James Faeldon, https://github.com/faeldon/philippines-json-maps/blob/master/2023/geojson/provdists/hires/municities-provdist-1307600000.0.1.json

m = folium.Map(
    location=[14.442855, 120.995621],
    zoom_start=12
)
with st.sidebar:
    color = st.color_picker(" ",value="#529334", label_visibility="collapsed")
    weight = st.slider(" ", min_value=1.0, max_value=10.0, value=5.0, step=0.1 ,label_visibility="collapsed")

folium.GeoJson(
    geojsondata,
    style_function=lambda feature: {
        "color": color,
        "fill": False,
        "weight": weight
    }
    ).add_to(m)

st_folium(m, width=700, height=700)