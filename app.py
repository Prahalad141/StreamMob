import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
import re
from datetime import datetime

# Streamlit page configuration
st.set_page_config(page_title="Admin Parking Dashboard", layout="wide")

# Custom CSS to mimic React Native dark theme
st.markdown("""
    <style>
    body {
        background-color: #0f172a;
        color: #ffffff;
    }
    .stApp {
        background-color: #0f172a;
    }
    .stTextInput > div > div > input {
        background-color: #1e293b;
        color: #ffffff;
        border-radius: 10px;
        border: 1px solid #3b82f6;
        padding: 10px;
    }
    .stButton > button {
        background-color: #ff6b6b;
        color: #ffffff;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        border: 2px solid #ffffff;
    }
    .stButton > button:hover {
        background-color: #ef4444;
    }
    .location-button, .slot-button {
        background-color: #4c66a0;
        color: #ffffff;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        text-align: center;
        cursor: pointer;
    }
    .location-button:hover, .slot-button:hover {
        background-color: #3b82f6;
    }
    .slot-booked {
        background-color: #ef4444;
    }
    .slot-in-progress {
        background-color: #1890ff;
    }
    .card {
        background-color: #6b7280;
        border-radius: 20px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        box-shadow: 0 5px 10px rgba(0, 0, 0, 0.3);
    }
    .section-title {
        font-size: 24px;
        font-weight: bold;
        margin: 20px 0 10px 0;
        color: #ffffff;
    }
    .header {
        background-color: #f6d365;
        border-radius: 0 0 80px 80px;
        padding: 20px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .header-minimized {
        padding: 10px;
        text-align: center;
    }
    .modal {
        background-color: #2c3e50;
        border-radius: 20px;
        padding: 20px;
        box-shadow: -5px 0 15px rgba(0, 0, 0, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# Data structures
if 'admin_database' not in st.session_state:
    st.session_state.admin_database = []
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'admin_name' not in st.session_state:
    st.session_state.admin_name = ''
if 'user_access_count' not in st.session_state:
    st.session_state.user_access_count = 1200
if 'live_data' not in st.session_state:
    st.session_state.live_data = [
        {"name": "Koramangala", "booked": 20, "vacant": 5, "inProgress": 2, "lat": 12.9352, "lon": 77.6140, "subLocations": []},
        {"name": "Whitefield", "booked": 18, "vacant": 7, "inProgress": 3, "lat": 12.9698, "lon": 77.7499, "subLocations": []},
        {"name": "Indiranagar", "booked": 15, "vacant": 10, "inProgress": 1, "lat": 12.9716, "lon": 77.6412, "subLocations": []},
        {"name": "MG Road", "booked": 12, "vacant": 8, "inProgress": 2, "lat": 12.9752, "lon": 77.6068, "subLocations": []},
        {"name": "Jayanagar", "booked": 10, "vacant": 5, "inProgress": 1, "lat": 12.9299, "lon": 77.5877, "subLocations": []},
        {"name": "HSR Layout", "booked": 14, "vacant": 6, "inProgress": 2, "lat": 12.9127, "lon": 77.6397, "subLocations": []},
        {"name": "Electronic City", "booked": 16, "vacant": 4, "inProgress": 3, "lat": 12.8481, "lon": 77.6433, "subLocations": []},
        {"name": "Bannerghatta Road", "booked": 13, "vacant": 7, "inProgress": 1, "lat": 12.8918, "lon": 77.5900, "subLocations": []},
        {"name": "Marathahalli", "booked": 11, "vacant": 9, "inProgress": 2, "lat": 12.9552, "lon": 77.6962, "subLocations": []},
        {"name": "UB City", "booked": 9, "vacant": 6, "inProgress": 1, "lat": 12.9724, "lon": 77.5953, "subLocations": []},
    ]
if 'booked_slots' not in st.session_state:
    st.session_state.booked_slots = {}
if 'selected_location' not in st.session_state:
    st.session_state.selected_location = None
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False
if 'is_header_minimized' not in st.session_state:
    st.session_state.is_header_minimized = False
if 'booking_details' not in st.session_state:
    st.session_state.booking_details = {"hours": "1", "slot_index": None, "car_name": "", "owner_name": ""}

# Predefined car and owner names
predefined_cars = [
    {"car_name": "Toyota Camry", "owner_name": "John Doe"},
    {"car_name": "Honda Civic", "owner_name": "Jane Smith"},
    {"car_name": "Ford Mustang", "owner_name": "Mike Johnson"},
    {"car_name": "BMW X5", "owner_name": "Sarah Williams"},
    {"car_name": "Audi A4", "owner_name": "David Brown"},
    {"car_name": "Mercedes C-Class", "owner_name": "Emily Davis"},
    {"car_name": "Volkswagen Golf", "owner_name": "Robert Taylor"},
    {"car_name": "Hyundai Sonata", "owner_name": "Lisa Anderson"},
    {"car_name": "Kia Optima", "owner_name": "James Wilson"},
    {"car_name": "Subaru Outback", "owner_name": "Mary Jones"},
    {"car_name": "Tesla Model 3", "owner_name": "Chris Evans"},
    {"car_name": "Jeep Wrangler", "owner_name": "Anna White"},
    {"car_name": "Chevrolet Malibu", "owner_name": "Paul Green"},
    {"car_name": "Nissan Altima", "owner_name": "Linda Clark"},
    {"car_name": "Mazda CX-5", "owner_name": "Thomas Lee"},
]

# Simulate live data updates
def update_live_data():
    for loc in st.session_state.live_data:
        loc["booked"] = max(0, loc["booked"] + (int(time.time() * 1000) % 3) - 1)
        loc["vacant"] = max(0, loc["vacant"] + (int(time.time() * 1000) % 3) - 1)
        loc["inProgress"] = max(0, loc["inProgress"] + (int(time.time() * 1000) % 2))
    st.session_state.user_access_count += (int(time.time() * 1000) % 10)
    st.experimental_rerun()

# Email validation
def validate_email(email):
    return re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email)

# Authentication
def auth_page():
    st.markdown("<div style='text-align: center; padding: 20px; background-color: rgba(44, 62, 80, 0.95); border-radius: 20px;'>", unsafe_allow_html=True)
    is_signup = st.checkbox("Sign Up (check for new account, uncheck for Sign In)")
    email = st.text_input("Email", placeholder="Enter email")
    password = st.text_input("Password", type="password", placeholder="Enter password")
    name = st.text_input("Full Name", placeholder="Enter full name") if is_signup else ""
    
    if st.button("Submit"):
        if not email or not password or (is_signup and not name):
            st.error("Please fill in all fields.")
        elif not validate_email(email):
            st.error("Please enter a valid email address.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters long.")
        elif is_signup:
            if any(admin["email"] == email for admin in st.session_state.admin_database):
                st.error("Email already registered.")
            else:
                st.session_state.admin_database.append({"email": email, "password": password, "name": name})
                st.session_state.admin_name = name
                st.session_state.is_authenticated = True
                st.success("Sign Up Successful!")
        else:
            admin = next((admin for admin in st.session_state.admin_database if admin["email"] == email and admin["password"] == password), None)
            if admin:
                st.session_state.admin_name = admin["name"] or email.split("@")[0]
                st.session_state.is_authenticated = True
                st.success("Sign In Successful!")
            else:
                st.error("Invalid email or password.")
    st.markdown("</div>", unsafe_allow_html=True)

# Main dashboard
def dashboard():
    # Header
    if st.session_state.is_header_minimized:
        st.markdown(f"<div class='header header-minimized'><button onclick='st.session_state.is_header_minimized=False;st.experimental_rerun()'>Expand</button></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='header'>
                <button onclick='st.session_state.is_header_minimized=True;st.experimental_rerun()'>Minimize</button>
                <div style='display: flex; align-items: center;'>
                    <span style='font-size: 28px; font-weight: bold; margin-left: 10px;'>Welcome, {st.session_state.admin_name}!</span>
                </div>
                <p style='color: #fff; font-size: 16px;'>Manage parking operations, monitor live updates, and optimize slot allocations.</p>
            </div>
        """, unsafe_allow_html=True)

    # Title
    st.markdown("<h1 class='section-title'>🚗 Admin Parking Dashboard</h1>", unsafe_allow_html=True)

    # Cards
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"<div class='card'><h3>Active Users</h3><h2>{st.session_state.user_access_count}</h2></div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='card'><h3>Full Locations</h3><h2>{sum(1 for loc in st.session_state.live_data if loc['vacant'] == 0)}</h2></div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<div class='card'><h3>In Progress</h3><h2>{sum(loc['inProgress'] for loc in st.session_state.live_data)}</h2></div>", unsafe_allow_html=True)

    # Pie Chart
    st.markdown("<h2 class='section-title'>📊 Booking Status</h2>", unsafe_allow_html=True)
    chart_data = pd.DataFrame([
        {"name": "Booked", "population": 650, "color": "#ff4d4f"},
        {"name": "Available", "population": 350, "color": "#52c41a"},
        {"name": "In Progress", "population": 100, "color": "#1890ff"},
    ])
    fig_pie = px.pie(chart_data, values="population", names="name", color="name", color_discrete_map={"Booked": "#ff4d4f", "Available": "#52c41a", "In Progress": "#1890ff"})
    fig_pie.update_layout(
        paper_bgcolor="rgba(30, 60, 114, 0.8)",
        plot_bgcolor="rgba(30, 60, 114, 0.8)",
        font_color="#ffffff",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Top 10 Places
    st.markdown("<h2 class='section-title'>📍 Top 10 Places</h2>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, loc in enumerate(st.session_state.live_data):
        with cols[i % 2]:
            if st.button(f"{loc['name']} (B: {loc['booked']}, V: {loc['vacant']})", key=f"loc-{loc['name']}", help="Click to view slots"):
                st.session_state.selected_location = loc

    # Bar Chart
    st.markdown("<h2 class='section-title'>📍 Bar Chart - Top 10 Places</h2>", unsafe_allow_html=True)
    bar_data = pd.DataFrame({
        "Location": [loc["name"] for loc in st.session_state.live_data],
        "Slots": [loc["booked"] + loc["vacant"] + loc["inProgress"] for loc in st.session_state.live_data]
    })
    fig_bar = px.bar(bar_data, x="Location", y="Slots", color_discrete_sequence=["#1890ff"])
    fig_bar.update_layout(
        paper_bgcolor="rgba(30, 60, 114, 0.8)",
        plot_bgcolor="rgba(30, 60, 114, 0.8)",
        font_color="#ffffff",
        xaxis_tickangle=30,
        yaxis_title="Slots",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Parking Slots
    if st.session_state.selected_location:
        loc = st.session_state.selected_location
        st.markdown(f"<h2 class='section-title'>{loc['name']} - Parking Slots</h2>", unsafe_allow_html=True)
        total_slots = (loc["booked"] + loc["vacant"] + loc["inProgress"]) * 2
        cols = st.columns(2)
        for column in range(2):
            with cols[column]:
                for i in range(loc["booked"] + loc["vacant"] + loc["inProgress"]):
                    adjusted_index = i + (column * (loc["booked"] + loc["vacant"] + loc["inProgress"]))
                    if adjusted_index >= total_slots:
                        continue
                    is_booked = adjusted_index < loc["booked"] * 2 or f"{loc['name']}-{adjusted_index}" in st.session_state.booked_slots
                    is_in_progress = adjusted_index >= loc["booked"] * 2 and adjusted_index < (loc["booked"] + loc["inProgress"]) * 2
                    slot_booking = st.session_state.booked_slots.get(f"{loc['name']}-{adjusted_index}", predefined_cars[adjusted_index % len(predefined_cars)] if adjusted_index < loc["booked"] * 2 else None)
                    if is_booked:
                        st.markdown(f"<div class='slot-button slot-booked'>🚗 Car: {slot_booking['car_name']}<br>Owner: {slot_booking['owner_name']}<br>Hours: {slot_booking.get('hours', '2')}</div>", unsafe_allow_html=True)
                    elif is_in_progress:
                        st.markdown("<div class='slot-button slot-in-progress'>In Progress</div>", unsafe_allow_html=True)
                    else:
                        if st.button("Empty Slot", key=f"slot-{loc['name']}-{adjusted_index}"):
                            st.session_state.show_modal = True
                            st.session_state.booking_details["slot_index"] = adjusted_index

    # Map View
    st.markdown("<h2 class='section-title'>🗺️ Map View</h2>", unsafe_allow_html=True)
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
    for loc in st.session_state.live_data:
        folium.Marker(
            [loc["lat"], loc["lon"]],
            popup=f"{loc['name']} (B: {loc['booked']}, V: {loc['vacant']})",
            icon=folium.Icon(color="red")
        ).add_to(m)
    st_folium(m, width="95%", height=250)

    # Modal for updating slots
    if st.session_state.show_modal and st.session_state.selected_location:
        with st.form("booking_form"):
            st.markdown("<div class='modal'>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: #fff;'>Update Parking Slot</h2>", unsafe_allow_html=True)
            hours = st.selectbox("Select Booking Hours", [f"{h} Hour{'s' if h > 1 else ''}" for h in range(1, 13)])
            car_name = st.text_input("Car Name", placeholder="Enter car name")
            owner_name = st.text_input("Owner Name", placeholder="Enter owner name")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Update Slot"):
                    if not hours or not car_name or not owner_name:
                        st.error("Please fill in all fields.")
                    else:
                        st.session_state.booked_slots[f"{st.session_state.selected_location['name']}-{st.session_state.booking_details['slot_index']}"] = {
                            "hours": hours.split()[0],
                            "car_name": car_name,
                            "owner_name": owner_name
                        }
                        st.session_state.show_modal = False
                        st.session_state.booking_details = {"hours": "1", "slot_index": None, "car_name": "", "owner_name": ""}
                        st.success(f"Slot updated for {hours}!")
                        st.experimental_rerun()
            with col2:
                if st.form_submit_button("Close"):
                    st.session_state.show_modal = False
                    st.session_state.booking_details = {"hours": "1", "slot_index": None, "car_name": "", "owner_name": ""}
            st.markdown("</div>", unsafe_allow_html=True)

# Main logic
if not st.session_state.is_authenticated:
    auth_page()
else:
    dashboard()

# Simulate live updates every 5 seconds
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()
if time.time() - st.session_state.last_update > 5:
    st.session_state.last_update = time.time()
    update_live_data()
