import carla


class PauseController:
    def __init__(self, vehicle, telemetry=None):
        self.vehicle = vehicle
        self.telemetry = telemetry
        self.paused = False
        self._stored_control = None
        self._stored_velocity = None
        self._stored_angular_velocity = None

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
        self._store_vehicle_state()
        self.vehicle.set_simulate_physics(False)

    def resume(self):
        if not self.paused:
            return
        self.paused = False
        if self.telemetry is not None:
            self.telemetry.resume()
        self.vehicle.set_simulate_physics(True)
        self._restore_vehicle_state()

    def _store_vehicle_state(self):
        try:
            self._stored_control = self.vehicle.get_control()
        except Exception:
            self._stored_control = None
        self._stored_velocity = self.vehicle.get_velocity()
        self._stored_angular_velocity = self.vehicle.get_angular_velocity()

    def _restore_vehicle_state(self):
        if self._stored_velocity is not None:
            self.vehicle.set_target_velocity(self._stored_velocity)
        if self._stored_angular_velocity is not None:
            self.vehicle.set_target_angular_velocity(self._stored_angular_velocity)
        if self._stored_control is not None:
            self.vehicle.apply_control(self._stored_control)
