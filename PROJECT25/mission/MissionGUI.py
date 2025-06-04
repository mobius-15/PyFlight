'''
Created on May 22, 2025

@author: redbu
'''
import streamlit as st
import sys
import os
import scipy
import pandas as pd
import pydeck as pdk
import json

# プロジェクトのルートをパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aircraft.FA18 import FA18
from planning.Waypoint import Waypoint
from planning.FlightPlan import FlightPlan
from mission.MissionContext import MissionContext
from logic.FlightLogic import log_segment_fuel, insert_landing_waypoint, simulate_carrier_launch
from vessels.Carrier import Carrier
from mission.PDFExport import export_mission_pdf
from io import BytesIO

st.set_page_config(layout="wide")
st.title("⚓ Carrier-Based Mission Planner")

# --- User Input Sidebar ---
st.sidebar.header("Mission Settings")
mission_type = st.sidebar.selectbox("Mission Type", ["CAP", "Strike", "Recon"])
cap_time = st.sidebar.slider("CAP Time (min)", 0, 120, 20)

# --- Carrier and Aircraft Setup ---
st.sidebar.subheader("Carrier Settings")
carrier_name = st.sidebar.text_input("Carrier Name", value="CVN-68 Nimitz")
carrier_lat = st.sidebar.number_input("Carrier Latitude", value=19.181, format="%.3f")
carrier_lon = st.sidebar.number_input("Carrier Longitude", value=134.139, format="%.3f")
carrier_heading = st.sidebar.number_input("Carrier Heading (°)", value=0.0, format="%.1f")
carrier = Carrier(name=carrier_name, lat=carrier_lat, lon=carrier_lon, heading_deg=carrier_heading)

fa18 = FA18()
launch = simulate_carrier_launch(fa18, carrier)

# --- Flight Plan Input ---
st.subheader("Flight Waypoints")
initial_wp_data = pd.DataFrame([
    {"alt": 200, "spd": 200, "dist": 5, "hdg": 180},
    {"alt": 5000, "spd": 280, "dist": 10, "hdg": 90},
    {"alt": 25000, "spd": 330, "dist": 90, "hdg": 110},
    {"alt": 28000, "spd": 280, "dist": 10, "hdg": 150},
    {"alt": 25000, "spd": 330, "dist": 90, "hdg": 290},
    {"alt": 2500, "spd": 260, "dist": 15, "hdg": 320},
])

wp_data = st.data_editor(initial_wp_data, use_container_width=True, num_rows="dynamic")


# --- Build Flight Plan ---
plan = FlightPlan()
wp0 = Waypoint(carrier.lat, carrier.lon, 0, 0, 0, carrier.heading_deg)
plan.add_waypoint(wp0)

for row in wp_data.itertuples():
    wp = Waypoint(0, 0, row.alt, row.spd, row.dist, row.hdg)
    wp.calculate_position(plan.waypoints[-1].latitude, plan.waypoints[-1].longitude)
    plan.add_waypoint(wp)

insert_landing_waypoint(plan, carrier, final_altitude=150)


# --- Mission Context ---
ctx = MissionContext(fa18, plan, mission_type)
ctx.compute_fuel_usage()
if mission_type == "CAP":
    ctx.insert_cap_phase(index=2, duration_min=cap_time)
ctx.compute_landing_weight()

# --- Output Table ---
st.subheader("Mission Segments")
segment_df = pd.DataFrame({
    "Segment": list(range(1, len(ctx.segment_fuel)+1)),
    "Phase": ctx.segment_phases,
    "Fuel Used (lb)": ctx.segment_fuel,
})
st.dataframe(segment_df, use_container_width=True)

st.metric("Total Flight Time (min)", f"{ctx.total_flight_time_min:.1f}")
st.metric("Landing Weight (lb)", f"{ctx.landing_weight:.1f}")

# --- Map ---
st.subheader("Flight Path")
coords = [{"lat": wp.latitude, "lon": wp.longitude} for wp in plan.waypoints]
map_df = pd.DataFrame(coords)
map_df['name'] = ['WP'+str(i) for i in range(len(map_df))]

line_data = pd.DataFrame({
    'source_lon': map_df['lon'][:-1].values,
    'source_lat': map_df['lat'][:-1].values,
    'target_lon': map_df['lon'][1:].values,
    'target_lat': map_df['lat'][1:].values
})

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=carrier.lat,
        longitude=carrier.lon,
        zoom=5,
        pitch=0,
    ),
    layers=[
        # ライン（経路）
        pdk.Layer(
            "LineLayer",
            data=line_data,
            get_source_position='[source_lon, source_lat]',
            get_target_position='[target_lon, target_lat]',
            get_color='[0, 100, 255]',
            get_width=3,
        ),
        # WPのマーカー表示
        pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[lon, lat]',
            get_fill_color='[255, 0, 0]',
            get_radius=2000,
        ),
        # WP名のラベル（任意）
        pdk.Layer(
            "TextLayer",
            data=map_df,
            get_position='[lon, lat]',
            get_text='name',
            get_size=16,
            get_color='[0, 0, 0]',
            get_angle=0,
            get_text_anchor='"middle"',
            get_alignment_baseline='"bottom"',
        ),
    ]
))

# --- Export Buttons ---
pdf_buffer = BytesIO()
export_mission_pdf(pdf_buffer, ctx, carrier)
pdf_data = pdf_buffer.getvalue()

csv_data = segment_df.to_csv(index=False)

json_data = ctx.flightplan.to_json(as_string=False)
json_str = json.dumps(json_data, indent=2)

col1, col2, col3 = st.columns(3)

with col1:
    st.download_button("📄 Download PDF Report", data=pdf_data, file_name="mission_report.pdf", mime="application/pdf")

with col2:
    st.download_button("📊 Download CSV Log", data=csv_data, file_name="fuel_log.csv", mime="text/csv")

with col3:
    st.download_button("🧾 Download Route JSON", data=json_str, file_name="route.json", mime="application/json")

