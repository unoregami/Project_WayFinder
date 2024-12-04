import folium
import streamlit as st
from streamlit_folium import st_folium
import urllib.request, json

geojsonlink = "https://raw.githubusercontent.com/unoregami/Project_WayFinder/refs/heads/main/pasay.json"    # From James Faeldon, https://github.com/faeldon/philippines-json-maps/blob/master/2023/geojson/provdists/hires/municities-provdist-1307600000.0.1.json
geojsondata = urllib.request.urlopen("https://raw.githubusercontent.com/unoregami/Project_WayFinder/refs/heads/main/pasay.json")   # Turn to HTTP request

data = json.load(geojsondata)
m = folium.Map(
    location=[14.442855, 120.995621],
    zoom_start=12
)
with st.sidebar:
    color = st.color_picker(" ",value="#529334", label_visibility="collapsed")
    weight = st.slider(" ", min_value=1.0, max_value=10.0, value=5.0, step=0.1 ,label_visibility="collapsed")

folium.GeoJson(
    geojsonlink,
    style_function=lambda feature: {
        "color": color,
        "fill": False,
        "weight": weight
    }
    ).add_to(m)

# data['features'][0]['geometry']['coordinates'][0][0]
# data['features'][0]['geometry']['coordinates'][1][0]
# 0 - lng; 1 - lat
combined = data['features'][0]['geometry']['coordinates'][0][0] + (data['features'][0]['geometry']['coordinates'][1][0])
max_lng, min_lng = combined[0][0], combined[0][0]
max_lat, min_lat = combined[0][1], combined[0][1]

# Get the max and min of lng & lat
for coords in combined:
    if coords[0] > max_lng:
        max_lng = coords[0]
    if coords[0] < min_lng:
        min_lng = coords[0]
    if coords[1] > max_lat:
        max_lat = coords[1]
    if coords[1] < min_lat:
        min_lat = coords[1]

st.write("Number of JSON coordinates", len(combined))
st.write(max_lng, max_lat, min_lng, min_lng)

folium.CircleMarker(location=[max_lat, max_lng],).add_to(m)
folium.CircleMarker(location=[min_lat, min_lng],).add_to(m)
folium.CircleMarker(location=[max_lat, min_lng],).add_to(m)
folium.CircleMarker(location=[min_lat, max_lng],).add_to(m)

folium.PolyLine(
    locations=[[max_lat, max_lng], [max_lat, min_lng], [min_lat, min_lng], [min_lat, max_lng], [max_lat, max_lng]],
    color='blue',
    weight=2,
    opacity=0.8
    ).add_to(m)

st_folium(m, width=700, height=700)
