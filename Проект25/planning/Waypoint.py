import math
import logic


class Waypoint:

    def __init__(self, latitude, longitude, altitude_ft, speed_kt, distance_nm, heading_deg):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude_ft = altitude_ft
        self.speed_kt = speed_kt
        self.distance_nm = distance_nm
        self.heading_deg = heading_deg
        
        if speed_kt>0:
            self.segment_time_min = distance_nm / speed_kt * 60  # 分
        else:
            self.segment_time_min=0.0
    
    def calculate_position(self, base_lat, base_lon):
        R_nm = 3440.065  # 地球半径 [NM]
        delta = self.distance_nm / R_nm
        theta = math.radians(self.heading_deg)
        base_lat_rad = math.radians(base_lat)
        base_lon_rad = math.radians(base_lon)
        new_lat = math.asin(math.sin(base_lat_rad) * math.cos(delta) +
                            math.cos(base_lat_rad) * math.sin(delta) * math.cos(theta))
        new_lon = base_lon_rad + math.atan2(math.sin(theta) * math.sin(delta) *
                            math.cos(base_lat_rad), math.cos(delta) - math.sin(base_lat_rad) * math.sin(new_lat))
        self.latitude = math.degrees(new_lat)
        self.longitude = math.degrees(new_lon)

    def __repr__(self):
        return f"WP(lat={self.latitude:.4f}, lon={self.longitude:.4f}, alt={self.altitude_ft}ft, spd={self.speed_kt}kt, hdg={self.heading_deg})"

