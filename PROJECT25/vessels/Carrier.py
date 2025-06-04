'''
Created on May 18, 2025

@author: redbu
'''
from vessels import BaseVessel


class Carrier(BaseVessel.Vessel):

    def __init__(self, name = "USS Nimitz", lat = 35.0, lon = 139.0, heading_deg = 90, speed_kt = 30, displacement_ton = 100000):
        super().__init__(name, lat, lon, heading_deg, speed_kt, displacement_ton)

    def launch_speed_threshold(self):
        return 170  # kt, CATOBAR
