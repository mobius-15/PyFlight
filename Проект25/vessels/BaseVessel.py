from dataclasses import dataclass


@dataclass
class Vessel:
    name: str
    lat: float
    lon: float
    heading_deg: int = 0
    speed_kt: int = 0
    displacement_ton: int = 0

    def get_position(self):
        return(self.lat, self.lon)

    def get_heading(self):
        return self.heading_deg

    def describe(self):
        return f"{self.name}({self.displacement_ton}t)@{self.lat:2f},{self.lon:2f}"
