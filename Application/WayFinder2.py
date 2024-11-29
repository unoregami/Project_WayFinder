import streamlit as st
import pwinput
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import pandas as pd
import openrouteservice
client = openrouteservice.Client(key="5b3ce3597851110001cf6248218a7e79a1614b9f8c36b43fa1467ee8")


def col(pos):
    col1, col2, col3 = st.columns(3)
    if pos == "R":
        return col3
    elif pos == "M":
        return col2
    else:
        return col1


def markerCreator(name, i):
    popup = folium.Popup(f"{i[0]}, {i[1]}")

    folium.Marker(
        location=[i[0], i[1]], 
        popup=popup,
        tooltip=name,
        icon=folium.Icon(color="green", icon="pager", prefix="fa")).add_to(marker_cluster)


#Plotting of Directions using opensourceservice API
def plotRoad(start_coords, end_coords):
    # Fetch directions (route) from OpenRouteService
    route = client.directions(
        coordinates=[list(reversed(start_coords)), list(reversed(end_coords))],
        radiuses=10390,
        profile='driving-car',
        format='geojson'
    )

    # Add the route as a PolyLine to the map
    folium.PolyLine(
        locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']],
        color='blue',
        weight=5,
        opacity=0.8
    ).add_to(m)

    # Add markers for start and end points
    folium.Marker(location=start_coords, popup="Start: Manila").add_to(m)
    folium.Marker(location=end_coords, popup="End: Makati").add_to(m)

    m.save("directions.html")
    print("Success!")


#Logo sizing
st.html("""
        <style>
        [alt=Logo] {
        height: 5rem;
        }
        </style>
        """)
st.logo('https://raw.githubusercontent.com/unoregami/Project_WayFinder/refs/heads/main/no%20bg.png', size="large")
col("M").header(":green[WayFinder]")

st.divider()

#Shows map
min_lat, max_lat = 14.386249, 14.4928
min_lon, max_lon = 120.957296, 121.03017

m = folium.Map(
    max_bounds = True,
    location=[14.442855, 120.995621], 
    zoom_start=13,
    min_zoom = 13,
    min_lat = min_lat,
    max_lat = max_lat,
    min_lon = min_lon,
    max_lon = max_lon)

#limits of map
folium.CircleMarker([14.442855, 120.995621],tooltip="Center").add_to(m)
folium.CircleMarker([max_lat, min_lon]).add_to(m)
folium.CircleMarker([min_lat, min_lon]).add_to(m)
folium.CircleMarker([min_lat, max_lon]).add_to(m)
folium.CircleMarker([max_lat, max_lon]).add_to(m)

#Las Pinas Border
#Insert code here

#Tricycle terminals marker
tric = "https://github.com/unoregami/Project_WayFinder/raw/refs/heads/main/Tricycle%20Terminal.xlsx"
term = "https://github.com/unoregami/Project_WayFinder/raw/refs/heads/main/Terminal.xlsx"
df = pd.read_excel(term)

coords = df[['Latitude', 'Longitude ']]

coordsArray = []
#get coordinates from coords and store in array
for i in range(len(coords)):
    ph = [coords["Latitude"][i], coords["Longitude "][i]]
    coordsArray.append(ph)

#Marker cluster
marker_cluster = MarkerCluster().add_to(m)
#places marker in the map
for i in range(len(coordsArray)):
    markerCreator(df["Terminal"][i], coordsArray[i],)


# Define start and end locations (latitude, longitude)
start_coords, end_coords = [14.391803, 121.009307], [14.486996, 120.981063]

plotRoad(start_coords, end_coords)

st_folium(m, width=700, height=700)

