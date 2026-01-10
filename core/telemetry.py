import math
import time
from datetime import datetime

import carla

from core.constants import DRIVE_AUTOMATIC, DRIVE_MANUAL
from core.route_metrics import RouteMetrics


class Telemetry:
    def __init__(
        self,
        world,
        vehicle,
        student_name,
        selected_mode,
        route,
        destination,
        takeover_controller=None,
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
        self._setup_sensors()

    def _get_elapsed_seconds(self, now=None):
        if now is None:
            now = time.time()
        paused_total = self.paused_total_seconds
        if self.paused and self.pause_started is not None:
            paused_total += now - self.pause_started
        elapsed = now - self.mission_start_time - paused_total
        return max(0.0, elapsed)

    def _setup_sensors(self):
        blueprint_library = self.world.get_blueprint_library()

        try:
            lane_bp = blueprint_library.find("sensor.other.lane_invasion")
            lane_sensor = self.world.spawn_actor(
                lane_bp, carla.Transform(), attach_to=self.vehicle
            )
            lane_sensor.listen(self._on_lane_invasion)
            self.lane_invasion_sensor = lane_sensor
        except Exception as e:
            print(f"[TELEMETRY][WARN] Lane invasion sensor failed: {e}")

        try:
            collision_bp = blueprint_library.find("sensor.other.collision")
            collision_sensor = self.world.spawn_actor(
                collision_bp, carla.Transform(), attach_to=self.vehicle
            )
            collision_sensor.listen(self._on_collision)
            self.collision_sensor = collision_sensor
        except Exception as e:
            print(f"[TELEMETRY][WARN] Collision sensor failed: {e}")

    def _on_lane_invasion(self, event):
        self.lane_invasion_count += 1

    def _on_collision(self, event):
        self.collision_count += 1
        impulse = event.normal_impulse
        intensity = math.sqrt(
            (impulse.x ** 2) + (impulse.y ** 2) + (impulse.z ** 2)
        )
        if intensity > self.collision_max_intensity:
            self.collision_max_intensity = intensity

    def update(self, active_drive_mode, dt):
        if self.paused or dt <= 0:
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
        elif active_drive_mode == DRIVE_AUTOMATIC:
            self.auto_time_seconds += dt
        self.route_metrics.update(location, dt)
        if self.takeover_controller is not None:
            if self.takeover_controller.takeover_requested:
                self.takeover_requested = True
            reaction = self.takeover_controller.get_reaction_time()
            if reaction is not None and self.takeover_reaction_time_seconds is None:
                self.takeover_reaction_time_seconds = reaction

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

    def record_mode_switch(self):
        self.mode_switch_count += 1

    def finalize(self):
        mission_duration_seconds = self._get_elapsed_seconds()
        average_speed_kmh = 0.0
        if self.speed_time_total > 0:
            average_speed_kmh = self.speed_time_sum / self.speed_time_total
        lane_center_offset_mean_meters = self.route_metrics.get_mean_offset()
        percent_time_in_lane = self.route_metrics.get_percent_in_route()
        takeover_requested_value = 1 if self.takeover_requested else 0
        takeover_reaction_value = "None"
        if takeover_requested_value == 1:
            reaction = self.takeover_reaction_time_seconds
            if reaction is None and self.takeover_controller is not None:
                reaction = self.takeover_controller.get_reaction_time()
            if reaction is not None:
                takeover_reaction_value = round(reaction, 2)
        return {
            "timestamp": self.timestamp,
            "student_name": self.student_name,
            "selected_mode": self.selected_mode,
            "mission_duration_seconds": round(mission_duration_seconds, 2),
            "distance_traveled_meters": round(self.distance_traveled_meters, 2),
            "average_speed_kmh": round(average_speed_kmh, 2),
            "max_speed_kmh": round(self.max_speed_kmh, 2),
            "lane_center_offset_mean_meters": round(lane_center_offset_mean_meters, 2),
            "percent_time_in_lane": round(percent_time_in_lane, 2),
            "lane_invasion_count": self.lane_invasion_count,
            "collision_count": self.collision_count,
            "collision_max_intensity": round(self.collision_max_intensity, 2),
            "manual_time_seconds": round(self.manual_time_seconds, 2),
            "auto_time_seconds": round(self.auto_time_seconds, 2),
            "mode_switch_count": self.mode_switch_count,
            "takeover_requested": takeover_requested_value,
            "takeover_reaction_time_seconds": takeover_reaction_value,
        }

    def cleanup(self):
        if self.lane_invasion_sensor is not None:
            self.lane_invasion_sensor.destroy()
            self.lane_invasion_sensor = None
        if self.collision_sensor is not None:
            self.collision_sensor.destroy()
            self.collision_sensor = None
