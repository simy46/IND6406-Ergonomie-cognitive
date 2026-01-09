import carla


class LaneMetrics:
    def __init__(self, carla_map):
        self.carla_map = carla_map
        self.offset_sum_time = 0.0
        self.total_time = 0.0
        self.in_lane_time = 0.0
        self.last_offset = 0.0
        self.last_in_lane = False
        self.last_lane_width = 0.0

    def update(self, location, dt):
        if location is None or dt <= 0:
            return
        waypoint = self.carla_map.get_waypoint(
            location,
            project_to_road=True,
            lane_type=carla.LaneType.Driving,
        )
        if waypoint is None:
            return
        wp_transform = waypoint.transform
        right = wp_transform.get_right_vector()
        dx = location.x - wp_transform.location.x
        dy = location.y - wp_transform.location.y
        dz = location.z - wp_transform.location.z
        offset = (dx * right.x) + (dy * right.y) + (dz * right.z)
        lane_width = waypoint.lane_width
        in_lane = False
        if lane_width and lane_width > 0:
            in_lane = abs(offset) <= (lane_width / 2.0)
        self.last_offset = offset
        self.last_in_lane = in_lane
        self.last_lane_width = lane_width if lane_width else 0.0
        self.offset_sum_time += abs(offset) * dt
        self.total_time += dt
        if in_lane:
            self.in_lane_time += dt

    def get_mean_offset(self):
        if self.total_time <= 0:
            return 0.0
        return self.offset_sum_time / self.total_time

    def get_percent_in_lane(self):
        if self.total_time <= 0:
            return 0.0
        return (self.in_lane_time / self.total_time) * 100.0
