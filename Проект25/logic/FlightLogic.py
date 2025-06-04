from scipy.integrate import solve_ivp
import numpy as np
from aircraft.FA18 import FA18
from logic import PhaseLogic

def simulate_carrier_launch(aircraft, vessel, ab_duration_sec=25):
    aircraft.afterburner = True
    fuel_used = aircraft.update_fuel(ab_duration_sec, throttle=1.0)
    speed_kt = vessel.launch_speed_threshold()

    return {
        "fuel_burned": fuel_used,
        "initial_speed": speed_kt,
        "duration_sec": ab_duration_sec
    }
def straight_segment_dynamics(t, y, speed_kt, heading_deg):
    # y = [x, y] in NM
    speed_nmps = speed_kt / 3600.0
    heading_rad = np.radians(heading_deg)
    dx = speed_nmps * np.cos(heading_rad)
    dy = speed_nmps * np.sin(heading_rad)
    return [dx, dy]


def simulate_segment(start_wp, end_wp):
    t_span = (0, end_wp.segment_time_min * 60)
    y0 = [start_wp.longitude, start_wp.latitude]
    args = (end_wp.speed_kt, end_wp.heading_deg)

    sol = solve_ivp(straight_segment_dynamics, t_span, y0, args = args, dense_output = True)
    return sol


def log_segment_fuel(waypoints, aircraft: FA18, alt_threshold = 3000,speed_threshold=30):
    fuel_log = []
    phase_log=[]
    
    if not hasattr(aircraft, "total_fuel"):
        aircraft.total_fuel = aircraft.remaining_fuel
    for i in range(1, len(waypoints)):
        wp_prev = waypoints[i - 1]
        wp_curr = waypoints[i]

        dt_min = wp_curr.segment_time_min
        dt_sec = dt_min * 60

        # フェーズ別ロジック（単純版）
        if wp_curr.altitude_ft > wp_prev.altitude_ft + alt_threshold:
            fuel = PhaseLogic.compute_climb_fuel(aircraft, dt_min)
            phase = "Climb"
        elif wp_curr.altitude_ft < wp_prev.altitude_ft - alt_threshold:
            fuel = PhaseLogic.compute_descent_fuel(aircraft, dt_min)
            phase = "Descent"
        elif wp_curr.speed_kt > wp_prev.speed_kt + speed_threshold:
            fuel = PhaseLogic.compute_acceleration_fuel(aircraft, dt_min)
            phase = "Acceleration"
        elif wp_curr.speed_kt < wp_prev.speed_kt - speed_threshold:
            fuel = PhaseLogic.compute_deceleration_fuel(aircraft, dt_min)
            phase = "Deceleration"
        else:
            # 巡航とみなす
            aircraft.afterburner = False
            fuel = aircraft.update_fuel(dt_min * 60, throttle=0.7)
            phase = "Cruise"

        # aircraft.afterburner = ab
        #
        # fuel_used = aircraft.update_fuel(dt_sec, throttle)

        fuel_log.append(fuel)
        phase_log.append(phase)

        # print(
        #     f"Segment {i}: Fuel used = {fuel:.1f} lb | Remaining = {aircraft.remaining_fuel:.1f} lb"
        # )

    return fuel_log,phase_log

def insert_landing_waypoint(flightplan,vessel,final_altitude=100):
    from planning.Waypoint import Waypoint
    
    wp_last=flightplan.waypoints[-1]
    wp_land=Waypoint(
        latitude=vessel.lat,
        longitude=vessel.lon,
        altitude_ft=final_altitude,
        speed_kt=140,
        distance_nm=0,
        heading_deg=vessel.heading_deg
        )
    flightplan.add_waypoint(wp_land)
