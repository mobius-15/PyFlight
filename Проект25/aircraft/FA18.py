class FA18:

    def __init__(self, use_afterburner = False):
        self.n_engine = 2
        self.thrust_mil = 11000 * self.n_engine  # N
        self.thrust_ab = 17700 * self.n_engine  # N
        self.sfc_mil = 0.81  # lb/lbf/hr
        self.sfc_ab = 1.74  # lb/lbf/hr
        self.afterburner = use_afterburner

        self.internal_fuel = 10800  # lb
        self.external_fuel = 3300  # lb（タンク1個相当）
        self.remaining_fuel = self.internal_fuel + self.external_fuel
        self.total_fuel = self.remaining_fuel

        self.empty_weight = 25100  # lb
        self.max_weight = 50200  # lb

    def get_thrust(self, throttle = 1.0):
        base_thrust = self.thrust_ab if self.afterburner else self.thrust_mil
        return base_thrust * throttle

    def get_sfc(self, throttle = 1.0):
        base_sfc = self.sfc_ab if self.afterburner else self.sfc_mil
        return base_sfc * throttle

    def get_fuel_flow(self, throttle = 1.0):
        thrust_lbf = self.get_thrust(throttle) * 0.22481  # N → lbf
        return thrust_lbf * self.get_sfc(throttle)  # lb/h

    def update_fuel(self, dt_seconds, throttle = 1.0):
        flow_rate = self.get_fuel_flow(throttle)  # lb/h
        burn = flow_rate * (dt_seconds / 3600)
        self.remaining_fuel = max(self.remaining_fuel - burn, 0)
        return burn

    def get_current_weight(self):
        return self.empty_weight + self.remaining_fuel
