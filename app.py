import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import time

st.set_page_config(
    page_title="JeepTrack PH",
    page_icon="🚐",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROUTES = ["Balagtas", "Alangilan", "Balete", "Soro-soro", "Lipa"]

ROUTE_COLORS = {
    "Balagtas": "#FF6B35",
    "Alangilan": "#004E89",
    "Balete": "#1AA260",
    "Soro-soro": "#F7B801",
    "Lipa": "#9C27B0"
}

BATANGAS_CENTER = [13.7565, 121.0583]

def init_session_state():
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_registered' not in st.session_state:
        st.session_state.user_registered = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'drivers' not in st.session_state:
        st.session_state.drivers = []
    if 'commuters' not in st.session_state:
        st.session_state.commuters = []
    if 'selected_jeepney' not in st.session_state:
        st.session_state.selected_jeepney = None

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def calculate_eta(driver_location, commuter_location):
    distance = geodesic(driver_location, commuter_location).kilometers
    avg_speed_kmh = 20
    eta_hours = distance / avg_speed_kmh
    eta_minutes = int(eta_hours * 60)
    return eta_minutes, round(distance, 2)

def role_selection_page():
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            color: #FF6B35;
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .sub-header {
            text-align: center;
            color: #004E89;
            font-size: 1.5rem;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="main-header">🚐 JeepTrack PH</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time Jeepney Tracking System</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 👋 Welcome! Please select your role:")
        
        col_driver, col_commuter = st.columns(2)
        
        with col_driver:
            if st.button("🚐 I'm a Driver", use_container_width=True, type="primary"):
                st.session_state.user_role = "driver"
                st.rerun()
        
        with col_commuter:
            if st.button("🧑 I'm a Commuter", use_container_width=True, type="secondary"):
                st.session_state.user_role = "commuter"
                st.rerun()

def driver_registration_page():
    st.markdown("## 🚐 Driver Registration")
    st.markdown("Please fill in your details to start tracking your jeepney")
    
    with st.form("driver_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", placeholder="Juan")
            last_name = st.text_input("Last Name *", placeholder="Dela Cruz")
            contact_number = st.text_input("Contact Number *", placeholder="09123456789")
            license_number = st.text_input("Driver's License Number *", placeholder="N01-12-345678")
        
        with col2:
            license_plate = st.text_input("Jeepney License Plate *", placeholder="ABC 1234")
            route = st.selectbox("Route *", ROUTES)
            max_capacity = st.number_input("Maximum Capacity (passengers) *", min_value=10, max_value=30, value=16)
            photo = st.file_uploader("Upload Your Photo *", type=["jpg", "jpeg", "png"])
        
        starting_lat = st.number_input("Starting Latitude", value=13.7565, format="%.6f", help="Your current location latitude")
        starting_lon = st.number_input("Starting Longitude", value=121.0583, format="%.6f", help="Your current location longitude")
        
        submitted = st.form_submit_button("Register as Driver", use_container_width=True, type="primary")
        
        if submitted:
            if not all([first_name, last_name, contact_number, license_number, license_plate, photo]):
                st.error("Please fill in all required fields marked with *")
            else:
                image = Image.open(photo)
                image.thumbnail((200, 200))
                image_b64 = image_to_base64(image)
                
                driver_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'contact_number': contact_number,
                    'license_number': license_number,
                    'license_plate': license_plate,
                    'route': route,
                    'max_capacity': max_capacity,
                    'current_capacity': 0,
                    'photo': image_b64,
                    'location': [starting_lat, starting_lon],
                    'registration_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.drivers.append(driver_data)
                st.session_state.user_data = driver_data
                st.session_state.user_registered = True
                st.success("✅ Registration successful! Redirecting to dashboard...")
                time.sleep(1)
                st.rerun()

def commuter_registration_page():
    st.markdown("## 🧑 Commuter Registration")
    st.markdown("Please fill in your details to start tracking jeepneys")
    
    with st.form("commuter_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", placeholder="Maria")
            last_name = st.text_input("Last Name *", placeholder="Santos")
        
        with col2:
            contact_number = st.text_input("Contact Number *", placeholder="09123456789")
            email = st.text_input("Email", placeholder="maria@example.com")
        
        current_lat = st.number_input("Your Current Latitude", value=13.7565, format="%.6f")
        current_lon = st.number_input("Your Current Longitude", value=121.0583, format="%.6f")
        
        submitted = st.form_submit_button("Register as Commuter", use_container_width=True, type="primary")
        
        if submitted:
            if not all([first_name, last_name, contact_number]):
                st.error("Please fill in all required fields marked with *")
            else:
                commuter_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'contact_number': contact_number,
                    'email': email,
                    'location': [current_lat, current_lon],
                    'registration_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.commuters.append(commuter_data)
                st.session_state.user_data = commuter_data
                st.session_state.user_registered = True
                st.success("✅ Registration successful! Redirecting to map...")
                time.sleep(1)
                st.rerun()

def driver_dashboard():
    st.markdown("## 🚐 Driver Dashboard")
    
    driver = st.session_state.user_data
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Route", driver['route'])
    with col2:
        st.metric("License Plate", driver['license_plate'])
    with col3:
        st.metric("Max Capacity", driver['max_capacity'])
    with col4:
        capacity_percent = (driver['current_capacity'] / driver['max_capacity']) * 100
        st.metric("Current Load", f"{driver['current_capacity']}/{driver['max_capacity']}", f"{capacity_percent:.0f}%")
    
    st.markdown("---")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### 📍 Update Your Location")
        new_lat = st.number_input("Latitude", value=float(driver['location'][0]), format="%.6f", key="driver_lat")
        new_lon = st.number_input("Longitude", value=float(driver['location'][1]), format="%.6f", key="driver_lon")
        
        if st.button("Update Location", type="primary"):
            driver['location'] = [new_lat, new_lon]
            for i, d in enumerate(st.session_state.drivers):
                if d['license_plate'] == driver['license_plate']:
                    st.session_state.drivers[i]['location'] = [new_lat, new_lon]
                    break
            st.success("Location updated successfully!")
            st.rerun()
    
    with col_right:
        st.markdown("### 👥 Update Passenger Capacity")
        new_capacity = st.slider(
            "Current Number of Passengers",
            min_value=0,
            max_value=driver['max_capacity'],
            value=driver['current_capacity'],
            key="capacity_slider"
        )
        
        if st.button("Update Capacity", type="primary"):
            driver['current_capacity'] = new_capacity
            for i, d in enumerate(st.session_state.drivers):
                if d['license_plate'] == driver['license_plate']:
                    st.session_state.drivers[i]['current_capacity'] = new_capacity
                    break
            st.success(f"Capacity updated to {new_capacity} passengers!")
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🗺️ Your Current Location on Map")
    
    driver_map = folium.Map(
        location=driver['location'],
        zoom_start=14,
        tiles="OpenStreetMap"
    )
    
    folium.Marker(
        driver['location'],
        popup=f"You are here - {driver['first_name']} {driver['last_name']}",
        tooltip="Your Location",
        icon=folium.Icon(color="red", icon="bus", prefix='fa')
    ).add_to(driver_map)
    
    st_folium(driver_map, width=None, height=400)

def commuter_map_view():
    st.markdown("## 🗺️ Live Jeepney Tracker")
    
    commuter = st.session_state.user_data
    
    st.sidebar.markdown("### 🎯 Filter by Route")
    selected_routes = []
    for route in ROUTES:
        if st.sidebar.checkbox(route, value=True, key=f"route_{route}"):
            selected_routes.append(route)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📍 Your Location")
    commuter_lat = st.sidebar.number_input("Latitude", value=float(commuter['location'][0]), format="%.6f", key="commuter_lat")
    commuter_lon = st.sidebar.number_input("Longitude", value=float(commuter['location'][1]), format="%.6f", key="commuter_lon")
    
    if st.sidebar.button("Update My Location", type="primary"):
        commuter['location'] = [commuter_lat, commuter_lon]
        st.success("Location updated!")
        st.rerun()
    
    filtered_drivers = [d for d in st.session_state.drivers if d['route'] in selected_routes]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👋 Welcome", f"{commuter['first_name']} {commuter['last_name']}")
    with col2:
        st.metric("🚐 Available Jeepneys", len(filtered_drivers))
    with col3:
        st.metric("🛣️ Routes Shown", len(selected_routes))
    
    st.markdown("---")
    
    jeepney_map = folium.Map(
        location=commuter['location'],
        zoom_start=13,
        tiles="OpenStreetMap"
    )
    
    folium.Marker(
        commuter['location'],
        popup="Your Location",
        tooltip="You are here",
        icon=folium.Icon(color="blue", icon="user", prefix='fa')
    ).add_to(jeepney_map)
    
    for driver in filtered_drivers:
        eta_minutes, distance = calculate_eta(driver['location'], commuter['location'])
        
        capacity_status = f"{driver['current_capacity']}/{driver['max_capacity']}"
        available_seats = driver['max_capacity'] - driver['current_capacity']
        
        popup_html = f"""
        <div style='width: 250px'>
            <h4 style='color: {ROUTE_COLORS[driver['route']]}; margin: 0;'>🚐 {driver['route']} Route</h4>
            <hr style='margin: 5px 0;'>
            <p><b>Driver:</b> {driver['first_name']} {driver['last_name']}</p>
            <p><b>License Plate:</b> {driver['license_plate']}</p>
            <p><b>Contact:</b> {driver['contact_number']}</p>
            <p><b>Capacity:</b> {capacity_status} passengers</p>
            <p><b>Available Seats:</b> {available_seats}</p>
            <p><b>Distance:</b> {distance} km</p>
            <p style='color: green; font-weight: bold;'>⏱️ ETA: {eta_minutes} minutes</p>
            <img src='data:image/png;base64,{driver['photo']}' width='200' style='border-radius: 8px;'>
        </div>
        """
        
        icon_color = 'green' if available_seats > 0 else 'red'
        
        folium.Marker(
            driver['location'],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{driver['route']} - {driver['license_plate']} (ETA: {eta_minutes} min)",
            icon=folium.Icon(color=icon_color, icon="bus", prefix='fa')
        ).add_to(jeepney_map)
    
    st_folium(jeepney_map, width=None, height=500)
    
    st.markdown("---")
    st.markdown("### 📋 Available Jeepneys")
    
    if filtered_drivers:
        for driver in filtered_drivers:
            eta_minutes, distance = calculate_eta(driver['location'], commuter['location'])
            available_seats = driver['max_capacity'] - driver['current_capacity']
            
            with st.expander(f"🚐 {driver['route']} - {driver['license_plate']} (ETA: {eta_minutes} min)"):
                col_info, col_photo = st.columns([2, 1])
                
                with col_info:
                    st.markdown(f"**Driver:** {driver['first_name']} {driver['last_name']}")
                    st.markdown(f"**Contact:** {driver['contact_number']}")
                    st.markdown(f"**License Number:** {driver['license_number']}")
                    st.markdown(f"**Route:** {driver['route']}")
                    st.markdown(f"**Capacity:** {driver['current_capacity']}/{driver['max_capacity']} passengers")
                    st.markdown(f"**Available Seats:** {available_seats}")
                    st.markdown(f"**Distance:** {distance} km")
                    st.markdown(f"**⏱️ ETA:** {eta_minutes} minutes")
                
                with col_photo:
                    st.image(f"data:image/png;base64,{driver['photo']}", caption="Driver Photo", use_container_width=True)
    else:
        st.info("No jeepneys available for selected routes")
    
    if st.sidebar.button("🔄 Refresh Map", use_container_width=True):
        st.rerun()

def main():
    init_session_state()
    
    st.markdown("""
        <style>
        .stButton>button {
            border-radius: 10px;
            font-weight: bold;
        }
        div[data-testid="metric-container"] {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.session_state.user_role is None:
        role_selection_page()
    
    elif not st.session_state.user_registered:
        if st.session_state.user_role == "driver":
            driver_registration_page()
        else:
            commuter_registration_page()
    
    else:
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.user_role = None
            st.session_state.user_registered = False
            st.session_state.user_data = {}
            st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"### 👤 Logged in as:")
        st.sidebar.markdown(f"**{st.session_state.user_data['first_name']} {st.session_state.user_data['last_name']}**")
        st.sidebar.markdown(f"**Role:** {st.session_state.user_role.capitalize()}")
        
        if st.session_state.user_role == "driver":
            driver_dashboard()
        else:
            commuter_map_view()

if __name__ == "__main__":
    main()
