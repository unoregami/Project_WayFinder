import openrouteservice.exceptions
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import pandas as pd
import openrouteservice
import requests
import urllib.request, json

# Load terminal data
term = "https://github.com/unoregami/Project_WayFinder/raw/refs/heads/main/Terminal.xlsx"   # fetch terminal coordinates
df = pd.read_excel(term)    # store in terminal coordinates
client = openrouteservice.Client(key="5b3ce3597851110001cf62482e908b8b20fe4b22a13bb5230018deb1")    # openrouteservice client
api_key = "AIzaSyDYf1vYZxJuJWPYhB24GdQ3n73-y1tLf14" #Google API key
geojsonlink = "https://raw.githubusercontent.com/unoregami/Project_WayFinder/refs/heads/main/pasay.json"    # From James Faeldon, https://github.com/faeldon/philippines-json-maps/blob/master/2023/geojson/provdists/hires/municities-provdist-1307600000.0.1.json
geojsondata = urllib.request.urlopen("https://raw.githubusercontent.com/unoregami/Project_WayFinder/refs/heads/main/pasay.json")   # Turn to HTTP request
data = json.load(geojsondata)   # Store json in data


# Tab naming
st.set_page_config(
    page_title="WayFinder",
    page_icon="https://raw.githubusercontent.com/unoregami/Project_WayFinder/refs/heads/main/no%20bg.png",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={"About": "https://github.com/unoregami/Project_WayFinder"}
    )


def markerCreator(name, i, c , cluster):
    popup = folium.Popup(f"{i[0]}, {i[1]}")
    folium.Marker(
        location=[i[0], i[1]],
        popup=popup,
        tooltip=name,
        icon=folium.Icon(color=c, icon="pager", prefix="fa")
    ).add_to(cluster)

def plotRoad(map_obj, start_coords, end_coords, st_name, en_name):
    # Fetch directions (route) from OpenRouteService
    try:
        route = client.directions(
            coordinates=[list(reversed(start_coords)), list(reversed(end_coords))],
            radiuses=10390,
            profile='driving-car',
            format='geojson'
        )
    except:
        st.session_state.distance = 0
        return st.error("End destination is too far.")

    st.session_state.distance = round(getDistance(route))

    # Add the route as a PolyLine to the map
    folium.PolyLine(
        locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']],
        color='blue',
        weight=5,
        opacity=0.8
    ).add_to(map_obj)

    # Add markers for start and end points
    folium.Marker(location=start_coords, popup=f"Start: {st_name}",
                    icon=folium.Icon(color="orange", icon="circle-dot", prefix="fa")).add_to(map_obj)
    folium.Marker(location=end_coords, popup=f"End: {en_name}",
                    icon=folium.Icon(color="red", icon='circle-dot', prefix='fa')).add_to(map_obj)

def getDistance(route):     # Get the distance
    distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000  # Convert meters to km
    return distance

def getFare(type):      # Calculate the Fare
    if type == "Jeep":
        baseFare = 13 # First 4 KMs
        rate = 1.8

        if st.session_state.distance <= 4:
            return baseFare
        addFare = (st.session_state.distance - 4) * rate
        return baseFare + addFare
    else:
        baseFare = 16 # For 1 KM
        rate = 5

        if st.session_state.distance <= 1:
            return baseFare
        addFare = (st.session_state.distance / 0.5) * rate
        return baseFare + addFare

def get_coordinates(api_key, address):  # Fetch coordinates using Google Maps API
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']['location']
            endName = data['results'][0]['formatted_address']
            return location['lat'], location['lng'], endName
        else:
            st.error("Address not found. Please try again.")
            return None, None, None
    else:
        st.error("Error with the API request.")
        return None, None, None

#---------------------------------------------------------------------------------------------------------------------------------------

def main():
    with st.sidebar:
        #Segmented Control Buttons
        #Choose a terminal
        termNames = [term for term in df["Terminal"]]
        options_map = {row[0]: row[1:] for row in df.to_numpy()}

        selection = st.segmented_control(
            f":green[Terminals]",
            options=list(options_map.keys()),
            format_func=lambda option: f"{option} ({options_map[option][2]})",
            selection_mode="single",
            default=list(options_map.keys())[0]
        )
        #options_map[termNames[index]][0-lat, 1-long, 2-type]
        selTermType = options_map[selection][2]
        selTermName = selection
        selTermCoords = [options_map[selection][0], options_map[selection][1]]

        color = st.color_picker(" ",value="#529334", label_visibility="collapsed")
        weight = st.slider(" ", min_value=1.0, max_value=10.0, value=5.0, step=0.1 ,label_visibility="collapsed")

    

    # Logo sizing
    st.html("""
            <style>
            [alt=Logo] {
            height: 5rem;
            }
            </style>
            """)
    st.logo('https://raw.githubusercontent.com/unoregami/Project_WayFinder/refs/heads/main/no%20bg.png', size="large")

    # Initialize map
    min_lat, max_lat = 14.386249, 14.4928       #Border of Las Piñas
    min_lon, max_lon = 120.957296, 121.03017
    m = folium.Map(
        max_bounds=True,
        location=[14.442855, 120.995621],
        zoom_start=12,
        #min_zoom=12,
        #min_lat=min_lat,
        #min_lon=min_lon,
        #max_lat=max_lat,
        #max_lon=max_lon
    )

    # Add LatLngPopup for clicking
    m.add_child(folium.LatLngPopup())

    # Add border markers
    folium.CircleMarker([14.442855, 120.995621], tooltip="Center", popup=folium.Popup("Center"),).add_to(m)

    # Las Piñas Border
    folium.GeoJson(
    geojsonlink,
    style_function=lambda feature: {
        "color": color,
        "fill": False,
        "weight": weight
    }
    ).add_to(m)

    # Store coordinates of terminal from csv
    coords = df[['Latitude', 'Longitude ']]
    coordsArray = [list(row) for row in coords.to_numpy()]

    # Marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    for i in range(len(coordsArray)):
        markerCreator(df["Terminal"][i], coordsArray[i], "green", marker_cluster)

    markerCreator(selTermName, selTermCoords, "orange", m)

    # Session State variables
    if "isDiscount" not in st.session_state:    # State for isDiscount
        st.session_state.isDiscount = False
    if "end_coords" not in st.session_state:    # State for end_coords
        st.session_state.end_coords = None
    if "distance" not in st.session_state:      # State for distance
        st.session_state.distance = 0
    if "map_output" not in st.session_state:    # State for map_output
        st.session_state.map_output = None
    if "endName" not in st.session_state:       # State for endName
        st.session_state.endName = None

    # Define default start location
    start_coords = [selTermCoords[0], selTermCoords[1]]

    # Text area for address input
    area = st.text_input("Enter an area name: ", autocomplete="off")
    if area:
        lat, lng, st.session_state.endName = get_coordinates(api_key, area)
        st.session_state.end_coords = [lat, lng]

    # Map on-clicked
    try:
        clicked_coords = st.session_state.map_output['last_clicked']
        if clicked_coords:
            st.session_state.end_coords = [clicked_coords['lat'], clicked_coords['lng']]
            st.session_state.endName = st.session_state.end_coords
    except:
        pass

    # Plot the route
    plotRoad(m, start_coords, st.session_state.end_coords, selTermName, st.session_state.endName)
    
    # Get the map with folium
    w = 700 #width of map
    h = 500 #height of map
    st.caption("Click on map where to go")
    st.session_state.map_output = st_folium(m, width=w, height=h)
    
    # Button for Priviledge Discount
    st.session_state.isDiscount = st.toggle("Privilege Discount for Senior Citizens, PWDs, and Students")

    # Get fare and show

    fare = round(getFare(selTermType))
    if st.session_state.isDiscount:
        fare = round(fare - int(fare * 0.2))
    st.write(":green[Fare]")
    st.subheader(f"{st.session_state.distance}km = :green[₱{fare}]")

if __name__ == "__main__":
    main()