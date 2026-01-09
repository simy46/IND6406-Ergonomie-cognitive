from agents.navigation.basic_agent import BasicAgent

from core.constants import AUTO_STEER_MAX_DELTA, AUTO_STEER_SMOOTHING


class AutonomousDriver:
    def __init__(self, vehicle, route):
        """
        route = output of compute_route()
        """
        self.vehicle = vehicle
        self.agent = BasicAgent(vehicle, target_speed=40)
        self._prev_steer = 0.0

        self.agent.set_global_plan(route, stop_waypoint_creation=True)

    def run_step(self):
        control = self.agent.run_step()
        control.steer = self._smooth_steer(control.steer)
        self.vehicle.apply_control(control)

    def is_done(self):
        return self.agent.done()

    def _smooth_steer(self, steer):
        delta = steer - self._prev_steer
        max_delta = AUTO_STEER_MAX_DELTA
        if delta > max_delta:
            steer = self._prev_steer + max_delta
        elif delta < -max_delta:
            steer = self._prev_steer - max_delta
        steer = (AUTO_STEER_SMOOTHING * steer) + ((1.0 - AUTO_STEER_SMOOTHING) * self._prev_steer)
        if steer > 1.0:
            steer = 1.0
        elif steer < -1.0:
            steer = -1.0
        self._prev_steer = steer
        return steer
