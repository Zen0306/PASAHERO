import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import pandas as pd
from datetime import datetime, timedelta
import base64
from io import BytesIO
from PIL import Image
import time
import database as db
import plotly.express as px
import plotly.graph_objects as go
import base64

with open("logo.png", "rb") as f:
    logo_data = f.read()
logo_base64 = base64.b64encode(logo_data).decode()

st.set_page_config(
    page_title="PASAHERO",
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

db.init_database()

def init_session_state():
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_registered' not in st.session_state:
        st.session_state.user_registered = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'active_trip' not in st.session_state:
        st.session_state.active_trip = None
    if 'show_analytics' not in st.session_state:
        st.session_state.show_analytics = False
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True

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
        .logo {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 500px;       
            margin-bottom: 0.5rem;
        }
        .sub-header {
            text-align: center;
            color: #004E89;
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="logo">', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Plan Your Jeepney Trips Faster and Safer!</p>', unsafe_allow_html=True)
    
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

def driver_login_page():
    st.markdown("## 🚐 Driver Login")
    st.markdown("Welcome back! Please enter your license plate to continue")
    
    with st.form("driver_login_form"):
        license_plate = st.text_input("Jeepney License Plate *", placeholder="ABC 1234")
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
        
        if submitted:
            if not license_plate:
                st.error("Please enter your license plate")
            else:
                driver = db.get_driver_by_license(license_plate)
                if driver:
                    st.session_state.user_data = driver
                    st.session_state.user_registered = True
                    st.success("✅ Login successful! Redirecting to dashboard...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ License plate not found. Please register first.")
    
    st.markdown("---")
    if st.button("Don't have an account? Register here", type="secondary"):
        st.session_state.show_login = False
        st.rerun()

def commuter_login_page():
    st.markdown("## 🧑 Commuter Login")
    st.markdown("Welcome back! Please enter your contact number to continue")
    
    with st.form("commuter_login_form"):
        contact_number = st.text_input("Contact Number *", placeholder="09123456789")
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
        
        if submitted:
            if not contact_number:
                st.error("Please enter your contact number")
            else:
                commuter = db.get_commuter_by_contact(contact_number)
                if commuter:
                    st.session_state.user_data = commuter
                    st.session_state.user_registered = True
                    st.success("✅ Login successful! Redirecting to map...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Contact number not found. Please register first.")
    
    st.markdown("---")
    if st.button("Don't have an account? Register here", type="secondary"):
        st.session_state.show_login = False
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
                    'location': [starting_lat, starting_lon]
                }
                
                driver_id = db.add_driver(driver_data)
                
                if driver_id:
                    driver_data['id'] = driver_id
                    st.session_state.user_data = driver_data
                    st.session_state.user_registered = True
                    st.success("✅ Registration successful! Redirecting to dashboard...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Registration failed. License plate or license number already exists.")
    
    st.markdown("---")
    if st.button("Already have an account? Login here", type="secondary"):
        st.session_state.show_login = True
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
                    'location': [current_lat, current_lon]
                }
                
                commuter_id = db.add_commuter(commuter_data)
                commuter_data['id'] = commuter_id
                st.session_state.user_data = commuter_data
                st.session_state.user_registered = True
                st.success("✅ Registration successful! Redirecting to map...")
                time.sleep(1)
                st.rerun()
    
    st.markdown("---")
    if st.button("Already have an account? Login here", type="secondary"):
        st.session_state.show_login = True
        st.rerun()

def trip_analytics_dashboard():
    st.markdown("## 📊 Trip Analytics Dashboard")
    
    driver = st.session_state.user_data
    trips = db.get_driver_trips(driver['id'])
    
    if not trips:
        st.info("No trip history yet. Start driving to see your analytics!")
        return
    
    completed_trips = [t for t in trips if t['status'] == 'completed']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Trips", driver.get('total_trips', 0))
    with col2:
        st.metric("Total Distance", f"{driver.get('total_distance', 0):.2f} km")
    with col3:
        avg_rating = driver.get('average_rating', 0)
        st.metric("Average Rating", f"⭐ {avg_rating:.1f}/5.0")
    with col4:
        st.metric("Total Reviews", driver.get('total_ratings', 0))
    
    st.markdown("---")
    
    if completed_trips:
        df_trips = pd.DataFrame(completed_trips)
        df_trips['start_time'] = pd.to_datetime(df_trips['start_time'])
        df_trips['date'] = df_trips['start_time'].dt.date
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("### 📈 Trips Over Time")
            daily_trips = df_trips.groupby('date').size().reset_index(name='trips')
            fig = px.line(daily_trips, x='date', y='trips', markers=True, 
                         title="Daily Trip Count", labels={'date': 'Date', 'trips': 'Number of Trips'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_chart2:
            st.markdown("### 🛣️ Distance Distribution")
            fig = px.histogram(df_trips, x='distance', nbins=20,
                              title="Trip Distance Distribution", 
                              labels={'distance': 'Distance (km)', 'count': 'Frequency'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📋 Recent Trips")
        recent_trips = completed_trips[:10]
        trip_table = []
        for trip in recent_trips:
            trip_table.append({
                'Date': trip['start_time'][:10],
                'Start Time': trip['start_time'][11:19],
                'End Time': trip['end_time'][11:19] if trip['end_time'] else 'N/A',
                'Distance (km)': f"{trip['distance']:.2f}",
                'Passengers': trip['passengers'],
                'Route': trip['route']
            })
        st.dataframe(pd.DataFrame(trip_table), use_container_width=True, hide_index=True)

def driver_reviews_section():
    st.markdown("### ⭐ Reviews & Ratings")
    
    driver = st.session_state.user_data
    reviews = db.get_driver_reviews(driver['id'])
    
    if not reviews:
        st.info("No reviews yet. Keep providing excellent service!")
        return
    
    avg_rating = driver.get('average_rating', 0)
    total_reviews = len(reviews)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"### ⭐ {avg_rating:.1f}/5.0")
        st.markdown(f"Based on {total_reviews} reviews")
    
    with col2:
        rating_counts = {i: 0 for i in range(1, 6)}
        for review in reviews:
            rating_counts[review['rating']] += 1
        
        for rating in range(5, 0, -1):
            count = rating_counts[rating]
            percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
            st.progress(percentage / 100, text=f"{'⭐' * rating} ({count})")
    
    st.markdown("---")
    st.markdown("#### Recent Reviews")
    
    for review in reviews[:5]:
        with st.container():
            col_rating, col_content = st.columns([1, 4])
            with col_rating:
                st.markdown(f"### {'⭐' * review['rating']}")
            with col_content:
                st.markdown(f"**{review['commuter_name']}** - {review['review_time'][:10]}")
                st.markdown(f"_{review['comment']}_")
            st.markdown("---")

def driver_dashboard():
    tab1, tab2, tab3 = st.tabs(["🚐 Dashboard", "📊 Analytics", "⭐ Reviews"])
    
    with tab1:
        driver_main_dashboard()
    
    with tab2:
        trip_analytics_dashboard()
    
    with tab3:
        driver_reviews_section()

def driver_main_dashboard():
    st.markdown("## 🚐 Driver Dashboard")
    
    driver = st.session_state.user_data
    driver_from_db = db.get_driver_by_license(driver['license_plate'])
    if driver_from_db:
        st.session_state.user_data.update(driver_from_db)
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
    
    col_left, col_middle, col_right = st.columns([1, 1, 1])
    
    with col_left:
        st.markdown("### 📍 Update Location")
        new_lat = st.number_input("Latitude", value=float(driver['location'][0]), format="%.6f", key="driver_lat")
        new_lon = st.number_input("Longitude", value=float(driver['location'][1]), format="%.6f", key="driver_lon")
        
        if st.button("Update Location", type="primary"):
            db.update_driver_location(driver['id'], new_lat, new_lon)
            driver['location'] = [new_lat, new_lon]
            st.success("Location updated!")
            st.rerun()
    
    with col_middle:
        st.markdown("### 👥 Update Capacity")
        new_capacity = st.slider(
            "Current Passengers",
            min_value=0,
            max_value=driver['max_capacity'],
            value=driver['current_capacity'],
            key="capacity_slider"
        )
        
        if st.button("Update Capacity", type="primary"):
            db.update_driver_capacity(driver['id'], new_capacity)
            driver['current_capacity'] = new_capacity
            st.success(f"Capacity updated to {new_capacity}!")
            st.rerun()
    
    with col_right:
        st.markdown("### 🛣️ Trip Management")
        
        if st.session_state.active_trip is None:
            if st.button("🚀 Start New Trip", type="primary", use_container_width=True):
                trip_id = db.start_trip(
                    driver['id'],
                    driver['location'][0],
                    driver['location'][1],
                    driver['route']
                )
                st.session_state.active_trip = trip_id
                st.success("Trip started!")
                st.rerun()
        else:
            st.info(f"Active Trip ID: {st.session_state.active_trip}")
            passengers = st.number_input("Passengers on this trip", min_value=0, max_value=driver['max_capacity'], value=driver['current_capacity'])
            
            if st.button("🏁 End Trip", type="secondary", use_container_width=True):
                trips = db.get_driver_trips(driver['id'])
                active_trip = next((t for t in trips if t['id'] == st.session_state.active_trip), None)
                
                if active_trip:
                    distance = geodesic(
                        (active_trip['start_lat'], active_trip['start_lon']),
                        (driver['location'][0], driver['location'][1])
                    ).kilometers
                    
                    db.end_trip(
                        st.session_state.active_trip,
                        driver['location'][0],
                        driver['location'][1],
                        distance,
                        passengers
                    )
                    st.session_state.active_trip = None
                    st.success(f"Trip ended! Distance: {distance:.2f} km")
                    st.rerun()
    
    st.markdown("---")
    st.markdown("### 🗺️ Your Current Location")
    
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
    
    drivers = db.get_all_drivers()
    filtered_drivers = [d for d in drivers if d['route'] in selected_routes]
    
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
        
        rating_display = f"⭐ {driver['average_rating']:.1f}" if driver['average_rating'] > 0 else "No ratings yet"
        
        popup_html = f"""
        <div style='width: 200px; font-size: 11px;'>
            <h4 style='color: {ROUTE_COLORS[driver['route']]}; margin: 0; font-size: 14px;'>🚐 {driver['route']}</h4>
            <hr style='margin: 3px 0;'>
            <p style='margin: 2px 0;'><b>Driver:</b> {driver['first_name']} {driver['last_name']}</p>
            <p style='margin: 2px 0;'><b>Plate:</b> {driver['license_plate']}</p>
            <p style='margin: 2px 0;'><b>Rating:</b> {rating_display}</p>
            <p style='margin: 2px 0;'><b>Seats:</b> {available_seats}/{driver['max_capacity']}</p>
            <p style='margin: 2px 0;'><b>Distance:</b> {distance} km</p>
            <p style='color: green; font-weight: bold; margin: 2px 0;'>⏱️ ETA: {eta_minutes} min</p>
            <img src='data:image/png;base64,{driver['photo']}' width='180' style='border-radius: 5px; margin-top: 5px;'>
        </div>
        """
        
        icon_color = 'green' if available_seats > 0 else 'red'
        
        folium.Marker(
            driver['location'],
            popup=folium.Popup(popup_html, max_width=250),
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
            
            rating_stars = f"⭐ {driver['average_rating']:.1f}/5.0 ({driver['total_ratings']} reviews)" if driver['average_rating'] > 0 else "No ratings yet"
            
            with st.expander(f"🚐 {driver['route']} - {driver['license_plate']} ({rating_stars}) - ETA: {eta_minutes} min"):
                col_info, col_photo = st.columns([2, 1])
                
                with col_info:
                    st.markdown(f"**Driver:** {driver['first_name']} {driver['last_name']}")
                    st.markdown(f"**Contact:** {driver['contact_number']}")
                    st.markdown(f"**License:** {driver['license_number']}")
                    st.markdown(f"**Route:** {driver['route']}")
                    st.markdown(f"**Capacity:** {driver['current_capacity']}/{driver['max_capacity']} passengers")
                    st.markdown(f"**Available Seats:** {available_seats}")
                    st.markdown(f"**Distance:** {distance} km")
                    st.markdown(f"**⏱️ ETA:** {eta_minutes} minutes")
                    st.markdown(f"**Rating:** {rating_stars}")
                    st.markdown(f"**Total Trips:** {driver['total_trips']}")
                    
                    st.markdown("---")
                    st.markdown("**Rate this driver:**")
                    
                    with st.form(f"review_form_{driver['id']}"):
                        rating = st.slider("Rating", 1, 5, 5, key=f"rating_{driver['id']}")
                        comment = st.text_area("Comment (optional)", key=f"comment_{driver['id']}", placeholder="Share your experience...")
                        
                        if st.form_submit_button("Submit Review"):
                            db.add_review(driver['id'], commuter['id'], rating, comment)
                            st.success("Thank you for your review!")
                            st.rerun()
                
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
            if st.session_state.show_login:
                driver_login_page()
            else:
                driver_registration_page()
        else:
            if st.session_state.show_login:
                commuter_login_page()
            else:
                commuter_registration_page()
    
    else:
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.user_role = None
            st.session_state.user_registered = False
            st.session_state.user_data = {}
            st.session_state.active_trip = None
            st.session_state.show_login = True
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
