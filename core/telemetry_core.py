import time
from datetime import datetime

from core.route_metrics import RouteMetrics


class TelemetryCore:
    def __init__(
        self,
        world,
        vehicle,
        student_name,
        selected_mode,
        route,
        destination,
        takeover_controller=None,
        nback_task=None,
    ):
        self.world = world
        self.vehicle = vehicle
        self.student_name = student_name
        self.selected_mode = selected_mode
        self.route = route
        self.destination = destination
        self.takeover_controller = takeover_controller
        self.mission_start_time = time.time()
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.distance_traveled_meters = 0.0
        self.prev_location = None
        self.speed_time_sum = 0.0
        self.speed_time_total = 0.0
        self.current_speed_kmh = 0.0
        self.max_speed_kmh = 0.0
        self.manual_time_seconds = 0.0
        self.auto_time_seconds = 0.0
        self.mode_switch_count = 0
        self.takeover_requested = False
        self.takeover_reaction_time_seconds = None
        self.collision_count = 0
        self.collision_max_intensity = 0.0
        self.lane_invasion_count = 0
        self.route_metrics = RouteMetrics(self.route)
        self.lane_invasion_sensor = None
        self.collision_sensor = None
        self.paused = False
        self.pause_started = None
        self.paused_total_seconds = 0.0
        self.nback_task = nback_task
        self._setup_sensors()

    def _get_elapsed_seconds(self, now=None):
        if now is None:
            now = time.time()
        paused_total = self.paused_total_seconds
        if self.paused and self.pause_started is not None:
            paused_total += now - self.pause_started
        elapsed = now - self.mission_start_time - paused_total
        return max(0.0, elapsed)

    def get_mission_elapsed_seconds(self):
        return self._get_elapsed_seconds()

    def update_route(self, route, destination, takeover_controller=None):
        self.route = route
        self.destination = destination
        self.route_metrics = RouteMetrics(self.route)
        if takeover_controller is not None:
            self.takeover_controller = takeover_controller

    def pause(self):
        if self.paused:
            return
        self.paused = True
        self.pause_started = time.time()

    def resume(self):
        if not self.paused:
            return
        now = time.time()
        if self.pause_started is not None:
            self.paused_total_seconds += now - self.pause_started
        self.paused = False
        self.pause_started = None
        self.prev_location = self.vehicle.get_location()

    def record_mode_switch(self):
        self.mode_switch_count += 1
