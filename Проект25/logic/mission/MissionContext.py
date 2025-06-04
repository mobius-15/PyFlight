from dataclasses import dataclass, field
from typing import List, Optional
from aircraft.FA18 import FA18
from planning import FlightPlan
from logic.PhaseLogic import compute_cap_fuel


@dataclass
class MissionContext:
    aircraft: FA18
    flightplan: FlightPlan
    mission_type: str
    segment_fuel: List[float] = field(default_factory = list)
    total_flight_time_min: float = 0.0
    cap_index: Optional[int] = None
    cap_duration_min: Optional[int] = None
    cap_fuel: Optional[float] = None
    landing_weight: Optional[float] = None
    segment_phases: List[str] = field(default_factory=list)

    def compute_fuel_usage(self):
        from logic.FlightLogic import log_segment_fuel
        self.segment_fuel, self.segment_phases = log_segment_fuel(self.flightplan.waypoints, self.aircraft)
        self.total_flight_time_min = sum(wp.segment_time_min for wp in self.flightplan.waypoints[1:])

    def insert_cap_phase(self, index: int, duration_min: int = 15):
        self.cap_index = index
        self.cap_duration_min = duration_min
        cap_burn = compute_cap_fuel(self.aircraft, duration_min)
        self.cap_fuel = cap_burn

        if self.segment_fuel:
            self.segment_fuel[index] += cap_burn
        else:
            self.segment_fuel = [0] * len(self.flightplan.waypoints)
            self.segment_fuel[index] = cap_burn

        self.total_flight_time_min += duration_min

    def compute_landing_weight(self):
        self.landing_weight = self.aircraft.get_current_weight()
        return self.landing_weight
