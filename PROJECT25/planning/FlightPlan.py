"""
Created on May 12, 2025

@author: redbu
"""

import uuid
import json


class FlightPlan:

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.waypoints = []

    def add_waypoint(self, wp):
        self.waypoints.append(wp)

    def update_coordinates(self, start_lat, start_lon):
        lat, lon = start_lat, start_lon
        for i, wp in enumerate(self.waypoints):
            if i == 0:
                wp.latitude, wp.longitude = lat, lon
            else:
                wp.calculate_position(lat, lon)
                lat, lon = wp.latitude, wp.longitude

    def to_json(self, as_string=False):
        data = [
            {
                "lat": round(wp.latitude, 6),
                "lon": round(wp.longitude, 6),
                "alt": wp.altitude_ft,
                "speed": wp.speed_kt,
                "dist": round(wp.distance_nm, 1),
                "hdg": wp.heading_deg
            }
            for wp in self.waypoints
        ]
        return json.dumps(data, indent=2) if as_string else data
    