import carla


class PauseController:
    def __init__(self, vehicle, telemetry=None):
        self.vehicle = vehicle
        self.telemetry = telemetry
        self.paused = False

    def set_telemetry(self, telemetry):
        self.telemetry = telemetry

    def toggle(self):
        if self.paused:
            self.resume()
        else:
            self.pause()

    def pause(self):
        if self.paused:
            return
        self.paused = True
        if self.telemetry is not None:
            self.telemetry.pause()
        self._apply_pause_control()

    def resume(self):
        if not self.paused:
            return
        self.paused = False
        if self.telemetry is not None:
            self.telemetry.resume()
        self._release_pause_control()

    def _apply_pause_control(self):
        self.vehicle.set_target_velocity(carla.Vector3D(0.0, 0.0, 0.0))
        self.vehicle.set_target_angular_velocity(carla.Vector3D(0.0, 0.0, 0.0))
        self.vehicle.apply_control(
            carla.VehicleControl(
                throttle=0.0,
                brake=1.0,
                steer=0.0,
                hand_brake=True,
                reverse=False,
            )
        )

    def _release_pause_control(self):
        self.vehicle.apply_control(
            carla.VehicleControl(
                throttle=0.0,
                brake=0.0,
                steer=0.0,
                hand_brake=False,
                reverse=False,
            )
        )
