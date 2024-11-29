import streamlit as st
import pwinput
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import pandas as pd

def col(pos):
    col1, col2, col3 = st.columns(3)
    if pos == "R":
        return col3
    elif pos == "M":
        return col2
    else:
        return col1

def accStatus():
    userList = account.keys()
    length = len(account)
    for i in userList:
        if user == account[i][0] and password == account[i][1]:
            col3.markdown(":green[Success Login]")
        elif len(user) == 0 and len(password) == 0:
            col3.markdown("")
        elif len(user) == 0 and len(password) > 0:
            col3.markdown("Please input username.")
        elif len(password) == 0 and len(user) > 0:
            col3.markdown("Please input password.")
        else:
            col3.markdown(":red[Failed Login]")

@st.dialog("Sign Up Page")
def signUpPage():
    with st.form("Sign Up"):
        fname = st.text_input("First Name: ", value="")
        #mmame = st.text_input("Middle Name: ", value="")
        #lname = st.text_input("Last Name: ", value="")
        signUser = st.text_input("Input Username: ", value="")
        signPass = st.text_input("Input Password: ", type='password', value="")
        signPassConf = st.text_input("Retype Password: ", type='password', value="")
        status = st.form_submit_button("Next")
        if status:
            if len(signUser) == 0 or signPass == 0 or len(fname) == 0: #or len(mmame) == 0 or len(lname) == 0:
                st.markdown(":red[Fill out the blank spaces]")
                status = False
            elif signPass != signPassConf:
                st.markdown(":orange[Passwords are mismatched! Please Try again.]")
            else:
                st.markdown(":green[Success]")
                st.session_state.newAcc = [fname, signUser, signPass]
                
                st.rerun()




def markerCreator(name, i):
    popup = folium.Popup(f"{i[0]}, {i[1]}")

    folium.Marker(
        location=[i[0], i[1]], 
        popup=popup,
        tooltip=name,
        icon=folium.Icon(color="green", icon="pager", prefix="fa")).add_to(marker_cluster)


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


#Login sample
if 'newAcc' not in st.session_state:
    st.session_state.newAcc = []

user, password, account = "", "", {}
account = {"uno": ["UnoEsparas", "12345"]}
user = st.text_input("Username: ", value="")
password = st.text_input("Password: ", value="", type='password')

#Login Button
col1, col2, col3 = st.columns(3) #col1 - left; col2 - middle; col3 - right
login = col2.button("Login", type='primary', on_click=accStatus(), use_container_width=True)
#Sign up
signup = col1.button("Sign up")

if signup:
    signUpPage()

test = st.button("Test")
if test:
    st.write(account)

st.write(f"Accounts: {account}")

st.divider()

#Shows map
min_lat, max_lat = 14.392645, 14.486404
min_lon, max_lon = 120.963692, 121.023774

m = folium.Map(
    max_bounds = True,
    location=[14.442855, 120.995621], 
    zoom_start=13,
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
df = pd.read_excel('https://github.com/unoregami/Project_WayFinder/raw/refs/heads/main/Tricycle%20Terminal.xlsx')
coords = df[["Latitude", "Longitude"]]

coordsArray = []
#get coordinates from coords and store in array
for i in range(len(coords)):
    ph = [coords["Latitude"][i], coords["Longitude"][i]]
    coordsArray.append(ph)

#Marker cluster
marker_cluster = MarkerCluster().add_to(m)
#places marker in the map
for i in range(len(coordsArray)):
    markerCreator(df["Terminal"][i], coordsArray[i],)


st_folium(m, width=700, height=700)

