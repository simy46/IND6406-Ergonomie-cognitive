import math

from core.constants import DRIVE_AUTONOMOUS, DRIVE_MANUAL


class TelemetryMetricsMixin:
    def update(self, active_drive_mode, dt, nback_click=False):
        if self.paused:
            return
        if self.nback_task is not None:
            self.nback_task.update(self._get_elapsed_seconds(), nback_click)
        if dt <= 0:
            return
        location = self.vehicle.get_location()
        if self.prev_location is not None:
            self.distance_traveled_meters += self.prev_location.distance(location)
        self.prev_location = location
        velocity = self.vehicle.get_velocity()
        speed = math.sqrt(
            (velocity.x ** 2) + (velocity.y ** 2) + (velocity.z ** 2)
        )
        speed_kmh = speed * 3.6
        self.current_speed_kmh = speed_kmh
        if speed_kmh > self.max_speed_kmh:
            self.max_speed_kmh = speed_kmh
        self.speed_time_sum += speed_kmh * dt
        self.speed_time_total += dt
        if active_drive_mode == DRIVE_MANUAL:
            self.manual_time_seconds += dt
        elif active_drive_mode == DRIVE_AUTONOMOUS:
            self.auto_time_seconds += dt
        self.route_metrics.update(location, dt)
        if self.takeover_controller is not None:
            if self.takeover_controller.takeover_requested:
                self.takeover_requested = True
            reaction = self.takeover_controller.get_reaction_time()
            if reaction is not None and self.takeover_reaction_time_seconds is None:
                self.takeover_reaction_time_seconds = reaction

    def get_lane_offset_mean(self):
        return self.route_metrics.get_mean_offset()

    def get_percent_in_lane(self):
        return self.route_metrics.get_percent_in_route()

    def get_takeover_reaction_time(self):
        if self.takeover_reaction_time_seconds is not None:
            return self.takeover_reaction_time_seconds
        if self.takeover_controller is not None:
            return self.takeover_controller.get_reaction_time()
        return None
