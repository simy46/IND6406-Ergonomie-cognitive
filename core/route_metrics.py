class RouteMetrics:
    def __init__(self, route, threshold_m=2.5):
        self.threshold_m = float(threshold_m)
        self.route_locations = []
        if route:
            for wp, _ in route:
                self.route_locations.append(wp.transform.location)
        self.offset_sum_time = 0.0
        self.total_time = 0.0
        self.in_route_time = 0.0
        self.last_offset = 0.0

    def update(self, location, dt):
        if location is None or dt <= 0 or not self.route_locations:
            return
        min_dist = None
        for loc in self.route_locations:
            dx = location.x - loc.x
            dy = location.y - loc.y
            dz = location.z - loc.z
            dist = (dx * dx + dy * dy + dz * dz) ** 0.5
            if min_dist is None or dist < min_dist:
                min_dist = dist
        if min_dist is None:
            return
        self.last_offset = min_dist
        self.offset_sum_time += min_dist * dt
        self.total_time += dt
        if min_dist <= self.threshold_m:
            self.in_route_time += dt

    def get_mean_offset(self):
        if self.total_time <= 0:
            return 0.0
        return self.offset_sum_time / self.total_time

    def get_percent_in_route(self):
        if self.total_time <= 0:
            return 0.0
        return (self.in_route_time / self.total_time) * 100.0
