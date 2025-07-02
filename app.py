import streamlit as st
import matplotlib.pyplot as plt

# Page setup with background styling
st.set_page_config(page_title="Smart Parking", layout="centered")

page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1350&q=80");
    background-size: cover;
    background-position: center;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.6);
    padding: 2rem;
    border-radius: 10px;
}
h1, h2, h3, label, .stTextInput>div>div>input, .stSelectbox>div>div>div>div {
    color: white !important;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚗 Smart Parking Dashboard</h1>", unsafe_allow_html=True)

# State management
if "booked_slots" not in st.session_state:
    st.session_state.booked_slots = {}
if "selected_slot" not in st.session_state:
    st.session_state.selected_slot = None
if "selected_location" not in st.session_state:
    st.session_state.selected_location = None

# Locations
locations = {
    "Koramangala": {"booked": 20, "vacant": 5},
    "Whitefield": {"booked": 18, "vacant": 7},
    "Indiranagar": {"booked": 15, "vacant": 10},
    "Jayanagar": {"booked": 25, "vacant": 2},
    "Malleshwaram": {"booked": 10, "vacant": 15},
}

# Location Selection
location = st.selectbox("📍 Select a Bengaluru Location", ["Select"] + list(locations.keys()))
if location != "Select":
    st.session_state.selected_location = location
    loc_data = locations[location]
    total_slots = loc_data["booked"] + loc_data["vacant"]
    st.markdown(f"<h3 style='color:white;'>🔒 Booked: {loc_data['booked']} | 🟢 Vacant: {loc_data['vacant']}</h3>", unsafe_allow_html=True)

    # Slot Display
    st.markdown("### 🅿️ Available Parking Slots")
    cols = st.columns(5)
    for i in range(total_slots):
        key = f"{location}-{i}"
        is_booked = i < loc_data["booked"] or st.session_state.booked_slots.get(key)
        slot_color = "#ff4d4f" if is_booked else "#52c41a"
        with cols[i % 5]:
            st.markdown(
                f"<button style='width:100%; background-color:{slot_color}; color:white; border:none; padding:8px; border-radius:5px;' {'disabled' if is_booked else ''} onclick='window.location.search=\"?slot={i}\"'>Slot {i+1}</button>",
                unsafe_allow_html=True
            )

    # Extract selected slot from query params
    selected_slot = st.experimental_get_query_params().get("slot", [None])[0]
    if selected_slot is not None:
        selected_slot = int(selected_slot)
        st.session_state.selected_slot = selected_slot

    # Booking Form
    if st.session_state.selected_slot is not None:
        st.markdown(f"### 📝 Booking Slot {st.session_state.selected_slot + 1}")
        with st.form("booking_form"):
            car_model = st.text_input("Car Model")
            car_number = st.text_input("Car Number")
            hours = st.selectbox("Select Hours", [str(i+1) for i in range(12)])
            submitted = st.form_submit_button("✅ Confirm Booking")

            if submitted:
                if car_model and car_number:
                    book_key = f"{location}-{st.session_state.selected_slot}"
                    st.session_state.booked_slots[book_key] = True
                    st.success(f"🎉 Slot {st.session_state.selected_slot + 1} booked at {location} for {hours} hour(s)")
                    st.session_state.selected_slot = None
                else:
                    st.warning("Please fill in all fields to book a slot.")

# Pie Chart
st.markdown("### 📊 Booking Insights")
labels = ['Booked', 'Available']
sizes = [650, 350]
colors = ['#ff4d4f', '#52c41a']
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, textprops={'color':"white"})
st.pyplot(fig)
