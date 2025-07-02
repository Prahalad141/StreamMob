import streamlit as st

# Page setup
st.set_page_config(page_title="Bengaluru Smart Parking", layout="wide")

# Styling
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1350&q=80");
    background-size: cover;
}
h1, h2, h3, label, .stTextInput>div>div>input, .stSelectbox>div>div>div>div {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚗 Bengaluru Smart Parking System</h1>", unsafe_allow_html=True)

# Session State
if "booked_slots" not in st.session_state:
    st.session_state.booked_slots = {}
if "selected_slot" not in st.session_state:
    st.session_state.selected_slot = None
if "location" not in st.session_state:
    st.session_state.location = None

# Area Data
areas = {
    "Koramangala": {
        "booked": 5, "vacant": 10,
        "updates": "Heavy traffic expected during weekends due to flea markets.",
        "sub_places": ["Sony World", "Forum Mall", "St. John's Hospital"]
    },
    "Whitefield": {
        "booked": 8, "vacant": 12,
        "updates": "Metro construction near ITPL might cause delays.",
        "sub_places": ["ITPL", "Phoenix Mall", "Hope Farm"]
    },
    "Indiranagar": {
        "booked": 6, "vacant": 9,
        "updates": "Night parking is now chargeable after 10 PM.",
        "sub_places": ["100ft Road", "Toit", "CMH Road"]
    },
    "Jayanagar": {
        "booked": 3, "vacant": 7,
        "updates": "Open air parking now available near 4th block.",
        "sub_places": ["Jayanagar 4th Block", "South End Circle", "RV Road"]
    },
    "Malleshwaram": {
        "booked": 2, "vacant": 6,
        "updates": "Street parking upgraded to smart meters.",
        "sub_places": ["Mantri Mall", "Sankey Tank", "8th Cross"]
    }
}

# Location selection
location = st.selectbox("📍 Choose a Bengaluru Location", ["Select"] + list(areas.keys()))
if location != "Select":
    st.session_state.location = location
    area = areas[location]
    total_slots = area["booked"] + area["vacant"]

    st.markdown(f"### 🔐 Booked: {area['booked']} | 🟢 Vacant: {area['vacant']} | 🅿️ Total: {total_slots}")
    st.info(f"📢 **Live Update:** {area['updates']}")
    st.success(f"📌 **Popular Spots:** {', '.join(area['sub_places'])}")

    # Show slots as buttons
    st.markdown("### 🚘 Parking Slots")
    cols = st.columns(5)
    for i in range(total_slots):
        key = f"{location}-{i}"
        is_booked = i < area["booked"] or st.session_state.booked_slots.get(key, False)
        color = "red" if is_booked else "green"
        label = f"Slot {i+1}"

        def make_callback(index=i):
            st.session_state.selected_slot = index

        with cols[i % 5]:
            if not is_booked:
                if st.button(f"🟢 {label}", key=key):
                    st.session_state.selected_slot = i
            else:
                st.markdown(f"<div style='background-color:{color}; color:white; padding:10px; text-align:center; border-radius:5px;'>{label} (Booked)</div>", unsafe_allow_html=True)

    # Booking form
    if st.session_state.selected_slot is not None:
        idx = st.session_state.selected_slot
        key = f"{location}-{idx}"

        st.markdown(f"### 📝 Booking Slot {idx + 1} at {location}")
        with st.form("booking_form"):
            model = st.text_input("Vehicle Model")
            number = st.text_input("Vehicle Number")
            hours = st.selectbox("How many hours?", [str(i+1) for i in range(12)])
            confirm = st.form_submit_button("💳 Pay & Confirm")

            if confirm:
                if model and number:
                    st.session_state.booked_slots[key] = True
                    st.success(f"✅ Slot {idx + 1} booked for {hours} hour(s) 🚘 ({model} - {number})")
                    st.balloons()
                    st.session_state.selected_slot = None
                else:
                    st.warning("❗ Please fill in all fields to book.")

