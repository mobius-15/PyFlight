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
carrier = Carrier(name="CVN-73", lat=34.5, lon=139.5, heading_deg=90)
fa18 = FA18()
launch = simulate_carrier_launch(fa18, carrier)

# --- Flight Plan Input ---
st.subheader("Flight Waypoints")
wp_data = st.data_editor(
    pd.DataFrame([
        {"alt": 25000, "spd": 450, "dist": 80, "hdg": 45},
        {"alt": 30000, "spd": 450, "dist": 100, "hdg": 90},
    ]),
    use_container_width=True,
    num_rows="dynamic"
)

# --- Build Flight Plan ---
wp0 = Waypoint(carrier.lat, carrier.lon, 0, 0, 0, 0)
wp1 = Waypoint(0, 0, 150, launch['initial_speed'], 0.5, carrier.heading_deg)
wp1.calculate_position(wp0.latitude, wp0.longitude)

plan = FlightPlan()
plan.add_waypoint(wp0)
plan.add_waypoint(wp1)

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

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=carrier.lat,
        longitude=carrier.lon,
        zoom=6,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "LineLayer",
            data=map_df,
            get_source_position='[lon, lat]',
            get_target_position='[lon, lat]',
            get_color='[0, 100, 255]',
            get_width=3,
        ),
        pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[lon, lat]',
            get_color='[255, 0, 0]',
            get_radius=2000,
        )
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

