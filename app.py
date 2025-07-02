import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Bengaluru Smart Parking", layout="wide")

# Background & UI styling
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-image: url('https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1350&q=80');
    background-size: cover;
}
h1, h2, h3, label, .stTextInput>div>div>input, .stSelectbox>div>div>div>div {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚗 Bengaluru Smart Parking System</h1>", unsafe_allow_html=True)

# Session state
if "booked_slots" not in st.session_state:
    st.session_state.booked_slots = {}
if "selected_slot" not in st.session_state:
    st.session_state.selected_slot = None
if "location" not in st.session_state:
    st.session_state.location = None

# Area data
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

location = st.selectbox("📍 Choose a Bengaluru Location", ["Select"] + list(areas.keys()))
if location != "Select":
    st.session_state.location = location
    area = areas[location]
    total_slots = area["booked"] + area["vacant"]

    st.markdown(f"### 🔐 Booked: {area['booked']} | 🟢 Vacant: {area['vacant']} | 🅿️ Total: {total_slots}")
    st.info(f"📢 **Live Update:** {area['updates']}")
    st.success(f"📌 **Popular Spots:** {', '.join(area['sub_places'])}")

    # Smart slot suggestion
    smart_slot = next((i for i in range(total_slots) if i >= area["booked"] and not st.session_state.booked_slots.get(f"{location}-{i}", False)), None)
    if smart_slot is not None:
        st.markdown(f"🧠 **Smart Suggestion**: Try booking Slot {smart_slot + 1}, it's vacant and closest to entry!")

    # Folium Map
    coords = {
        "Koramangala": (12.9352, 77.6140),
        "Whitefield": (12.9698, 77.7499),
        "Indiranagar": (12.9716, 77.6412),
        "Jayanagar": (12.9250, 77.5938),
        "Malleshwaram": (13.0057, 77.5696),
    }
    st.markdown("### 🗺️ Live Parking Map View")
    m = folium.Map(location=coords[location], zoom_start=14)
    folium.Marker(location=coords[location], popup=location, tooltip="Center Location", icon=folium.Icon(color="red")).add_to(m)
    st_data = st_folium(m, width=700, height=450)

    # Pie Chart
    st.markdown("## 📈 Area Insights and Visualization")
    pie_fig = go.Figure(data=[go.Pie(labels=["Booked", "Vacant"], values=[area["booked"], area["vacant"]],
                                     marker=dict(colors=["#ff4d4f", "#52c41a"]))])
    pie_fig.update_layout(title="📊 Slot Distribution")
    st.plotly_chart(pie_fig, use_container_width=True)

    # Bar Chart across locations
    booked_vals = [areas[loc]['booked'] for loc in areas]
    vacant_vals = [areas[loc]['vacant'] for loc in areas]
    fig = go.Figure(data=[
        go.Bar(name='Booked', x=list(areas.keys()), y=booked_vals, marker_color='red'),
        go.Bar(name='Vacant', x=list(areas.keys()), y=vacant_vals, marker_color='green')
    ])
    fig.update_layout(
        title="🚦 Slot Status across Areas",
        barmode='group',
        xaxis_title="Locations",
        yaxis_title="No. of Slots",
    )
    st.plotly_chart(fig, use_container_width=True)

    # 3D Popular Sub Places
    subs = [(loc, place) for loc in areas for place in areas[loc]['sub_places']]
    sub_df = pd.DataFrame(subs, columns=["Area", "SubPlace"])
    sub_df["PopularityScore"] = [len(name) % 10 + 5 for name in sub_df["SubPlace"]]
    fig3d = go.Figure(data=[go.Scatter3d(
        x=sub_df["Area"],
        y=sub_df["SubPlace"],
        z=sub_df["PopularityScore"],
        mode='markers+text',
        marker=dict(size=sub_df["PopularityScore"], color=sub_df["PopularityScore"], colorscale='Viridis'),
        text=sub_df["SubPlace"]
    )])
    fig3d.update_layout(
        scene=dict(xaxis_title='Area', yaxis_title='Sub Place', zaxis_title='Popularity'),
        title="📍 Sub-Places Popularity (3D)"
    )
    st.plotly_chart(fig3d, use_container_width=True)

    # Parking Slots Grid
    st.markdown("### 🚘 Parking Slots")
    cols = st.columns(5)
    for i in range(total_slots):
        key = f"{location}-{i}"
        is_booked = i < area["booked"] or st.session_state.booked_slots.get(key, False)
        label = f"Slot {i+1}"
        with cols[i % 5]:
            if not is_booked:
                if st.button(f"🟢 {label}", key=key):
                    st.session_state.selected_slot = i
            else:
                st.markdown(
                    f"<div style='background-color:red; color:white; padding:10px; text-align:center; border-radius:5px;'>{label} (Booked)</div>",
                    unsafe_allow_html=True
                )

    # 3D View of Slots
    st.markdown("### 🧱 3D View of Parking Slots")
    slot_status = []
    for i in range(total_slots):
        key = f"{location}-{i}"
        is_booked = i < area["booked"] or st.session_state.booked_slots.get(key, False)
        slot_status.append({
            "Slot": f"Slot {i+1}",
            "Row": i // 5,
            "Col": i % 5,
            "Status": "Booked" if is_booked else "Vacant",
            "Color": "#ff4d4f" if is_booked else "#52c41a"
        })
    df_slots = pd.DataFrame(slot_status)
    slot_fig = go.Figure(data=[go.Scatter3d(
        x=df_slots["Col"],
        y=df_slots["Row"],
        z=[1]*len(df_slots),
        mode='markers+text',
        marker=dict(size=12, color=df_slots["Color"]),
        text=df_slots["Slot"],
        textposition="top center"
    )])
    slot_fig.update_layout(
        scene=dict(xaxis_title="Column", yaxis_title="Row", zaxis_title="Level"),
        title="🅿️ 3D Parking Grid Visualization"
    )
    st.plotly_chart(slot_fig, use_container_width=True)

    # Booking form
    if st.session_state.selected_slot is not None:
        idx = st.session_state.selected_slot
        key = f"{location}-{idx}"
        st.markdown(f"### 📝 Booking Slot {idx + 1} at {location}")
        with st.form("booking_form"):
            model = st.text_input("Vehicle Model")
            number = st.text_input("Vehicle Number")
            hours = st.selectbox("How many hours?", [str(i+1) for i in range(12)])
            fee_per_hour = 50
            total_cost = int(hours) * fee_per_hour
            st.info(f"💰 Estimated Cost: ₹{total_cost}")
            confirm = st.form_submit_button("💳 Pay & Confirm")
            if confirm:
                if model and number:
                    st.session_state.booked_slots[key] = True
                    st.success(
                        f"✅ Slot {idx + 1} booked for {hours} hour(s) 🚘 ({model} - {number})\n💳 Total: ₹{total_cost}")
                    st.balloons()
                    st.session_state.selected_slot = None
                else:
                    st.warning("❗ Please fill in all fields to book.")
