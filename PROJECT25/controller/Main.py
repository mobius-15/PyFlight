from scipy.integrate import solve_ivp
import numpy as np
from planning import FlightPlan
from planning import Waypoint
from logic.FlightLogic import log_segment_fuel
from logic.FlightLogic import simulate_carrier_launch
from logic.FlightLogic import insert_landing_waypoint
from aircraft.FA18 import FA18 
from mission.MissionContext import MissionContext
from vessels.Carrier import Carrier
from _plotly_utils.colors.cmocean import phase
from flask import ctx


if __name__ == "__main__":
    carrier=Carrier(name="CVN-73",lat=19.19,lon=134.1,heading_deg =180)

    fa18 = FA18()
    # fuel_log = log_segment_fuel(plan.waypoints, fa18)
    launch=simulate_carrier_launch(fa18,carrier)
 
    
        # Waypoint作成
    wp0 = Waypoint.Waypoint(carrier.lat, carrier.lon, 0, 0, 0, 0)
    wp1 = Waypoint.Waypoint(0, 0, 150, launch['initial_speed'], 0.5, carrier.heading_deg)
    wp1.calculate_position(wp0.latitude, wp0.longitude)
    wp2 = Waypoint.Waypoint(0, 0, 30000, 450, 100, 90)
    wp2.calculate_position(wp1.latitude, wp1.longitude)
    
    wps=[wp0,wp1,wp2]

    plan = FlightPlan.FlightPlan()
    for wp in wps:
        plan.add_waypoint(wp)
    plan.update_coordinates(wps[0].latitude, wps[0].longitude)
    
    insert_landing_waypoint(plan, carrier, final_altitude=150)

    ctx = MissionContext(fa18, plan, mission_type = "CAP")

    ctx.compute_fuel_usage()
    ctx.insert_cap_phase(index = 1, duration_min = 60)
    ctx.compute_landing_weight()
print(f"Launched from {carrier.name} | Fuel burned: {launch['fuel_burned']:.1f} lb")
print(f"Mission ID: {plan.id}")

for i, (fuel, phase) in enumerate(zip(ctx.segment_fuel, ctx.segment_phases), 1):
    print(f"Segment {i}: Phase={phase}, Fuel used={fuel:.1f} lb")

print(f"Total flight time: {ctx.total_flight_time_min:.1f} min")
print(f"Landing weight: {ctx.landing_weight:.1f} lb")