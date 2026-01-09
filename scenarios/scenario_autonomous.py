from agents.navigation.basic_agent import BasicAgent


class AutonomousDriver:
    def __init__(self, vehicle, route):
        """
        route = output of compute_route()
        """
        self.vehicle = vehicle
        self.agent = BasicAgent(vehicle, target_speed=40)

        self.agent.set_global_plan(route, stop_waypoint_creation=True)

    def run_step(self):
        control = self.agent.run_step()
        self.vehicle.apply_control(control)

    def is_done(self):
        return self.agent.done()
