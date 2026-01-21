import math

import carla


class TelemetrySensorsMixin:
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

    def cleanup(self):
        if self.lane_invasion_sensor is not None:
            self.lane_invasion_sensor.destroy()
            self.lane_invasion_sensor = None
        if self.collision_sensor is not None:
            self.collision_sensor.destroy()
            self.collision_sensor = None
