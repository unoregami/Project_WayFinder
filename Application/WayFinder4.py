import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import pandas as pd
import openrouteservice


client = openrouteservice.Client(key="5b3ce3597851110001cf62482e908b8b20fe4b22a13bb5230018deb1")


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
    route = client.directions(
        coordinates=[list(reversed(start_coords)), list(reversed(end_coords))],
        radiuses=10390,
        profile='driving-car',
        format='geojson'
    )

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

def getDistance(route):
    distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000  # Convert meters to km
    return distance

def getFare(type):
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


def main():
    # Logo sizing
    st.html("""
            <style>
            [alt=Logo] {
            height: 5rem;
            }
            </style>
            """)
    st.logo('https://raw.githubusercontent.com/unoregami/Project_WayFinder/refs/heads/main/no%20bg.png', size="large")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.title(":green[WayFinder]")
    st.divider()

    # Initialize map
    min_lat, max_lat = 14.386249, 14.4928
    min_lon, max_lon = 120.957296, 121.03017

    m = folium.Map(
        max_bounds=True,
        location=[14.442855, 120.995621],
        zoom_start=12,
        min_zoom=12,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon
    )

    # Add LatLngPopup for clicking
    m.add_child(folium.LatLngPopup())

    # Add border markers
    folium.CircleMarker([14.442855, 120.995621], tooltip="Center").add_to(m)
    folium.CircleMarker([max_lat, min_lon]).add_to(m)
    folium.CircleMarker([min_lat, min_lon]).add_to(m)
    folium.CircleMarker([min_lat, max_lon]).add_to(m)
    folium.CircleMarker([max_lat, max_lon]).add_to(m)

    # Load terminal data
    term = "https://github.com/unoregami/Project_WayFinder/raw/refs/heads/main/Terminal.xlsx"
    df = pd.read_excel(term)
    

    coords = df[['Latitude', 'Longitude ']]
    coordsArray = [list(row) for row in coords.to_numpy()]

    # Marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    for i in range(len(coordsArray)):
        markerCreator(df["Terminal"][i], coordsArray[i], "green", marker_cluster)

    #Segmented Control Buttons
    #Choose a terminal
    termNames = [term for term in df["Terminal"]]
    options_map = {row[0]: row[1:] for row in df.to_numpy()}

    selection = st.segmented_control(
        "Terminals",
        options=list(options_map.keys()),
        format_func=lambda option: f"{option} ({options_map[option][2]})",
        selection_mode="single",
    )

    #options_map[termNames[index]][0-lat, 1-long, 2-type]
    if selection is None:
        selTermName = termNames[0]
        selTermCoords = [options_map[termNames[0]][0], options_map[termNames[0]][1]]
        selTermType = options_map[termNames[0]][2]
    else:
        selTermName = selection
        selTermCoords = options_map[selection]
        selTermType = options_map[selection][2]

    markerCreator(selTermName, selTermCoords, "orange", m)

    if "isDiscount" not in st.session_state:
        st.session_state.isDiscount = False

    st.session_state.isDiscount = st.toggle("Privilege Discount for Senior Citizens, PWDs, and Students")


    # Define default start location
    start_coords = [selTermCoords[0], selTermCoords[1]]

    # State for end_coords
    if "end_coords" not in st.session_state:
        st.session_state.end_coords = None

    # State for km distance
    if "distance" not in st.session_state:
        st.session_state.distance = 0

    #Columns for the maps       
    col1, col2 = st.columns(2)

    # Get the map with folium
    w = 350 #width of map
    h = 500 #height of map
    with col1:
        st.caption("Click on map where to go")
        map_output = st_folium(m, width=w, height=h)

    # Get on-click coordinates and update the map
    if map_output and 'last_clicked' in map_output:
        clicked_coords = map_output['last_clicked']

        if clicked_coords:
            st.session_state.end_coords = [clicked_coords['lat'], clicked_coords['lng']]
            
            m = folium.Map(
                max_bounds=True,
                location=[14.442855, 120.995621],
                zoom_start=12,
                min_zoom=12,
                min_lat=min_lat,
                max_lat=max_lat,
                min_lon=min_lon,
                max_lon=max_lon
            )
            marker_cluster = MarkerCluster().add_to(m)
            for i in range(len(coordsArray)):
                markerCreator(df["Terminal"][i], coordsArray[i], "green", marker_cluster)
            
            # Plot the route
            plotRoad(m, start_coords, st.session_state.end_coords, selection, st.session_state.end_coords)
            
            fare = round(getFare(selTermType))
            if st.session_state.isDiscount:
                fare = round(fare - int(fare * 0.2))
            st.write(":green[Fare]")
            st.subheader(f"{st.session_state.distance}km = :green[₱{fare}]")

            # Update the map
            with col2:
                st.caption("Directions")
                map_output = st_folium(m, width=w, height=h)


if __name__ == "__main__":
    main()