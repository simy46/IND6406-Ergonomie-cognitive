import random
import carla


class TrafficController:
    def __init__(self, client, world, vehicle_count, walker_count):
        self.client = client
        self.world = world
        self.vehicle_count = int(vehicle_count)
        self.walker_count = int(walker_count)
        self.actors = []

    def apply(self, enabled):
        if enabled:
            if not self.actors:
                self._spawn_traffic()
        else:
            self.destroy_all()

    def destroy_all(self):
        if not self.actors:
            return
        for actor in self.actors:
            try:
                actor.destroy()
            except Exception:
                pass
        self.actors = []

    def _spawn_traffic(self):
        self.destroy_all()
        blueprint_library = self.world.get_blueprint_library()
        spawn_points = self.world.get_map().get_spawn_points()
        random.shuffle(spawn_points)

        traffic_manager = self.client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(False)

        vehicle_bps = blueprint_library.filter("vehicle.*")
        for spawn_point in spawn_points[: self.vehicle_count]:
            bp = random.choice(vehicle_bps)
            if bp.has_attribute("color"):
                color = random.choice(bp.get_attribute("color").recommended_values)
                bp.set_attribute("color", color)
            try:
                vehicle = self.world.spawn_actor(bp, spawn_point)
            except RuntimeError:
                continue
            vehicle.set_autopilot(True, traffic_manager.get_port())
            self.actors.append(vehicle)

        walker_bps = blueprint_library.filter("walker.pedestrian.*")
        walker_controller_bp = blueprint_library.find("controller.ai.walker")
        walker_spawn_points = []
        for _ in range(self.walker_count):
            location = self.world.get_random_location_from_navigation()
            if location:
                walker_spawn_points.append(carla.Transform(location))
        for spawn_point in walker_spawn_points:
            bp = random.choice(walker_bps)
            try:
                walker = self.world.spawn_actor(bp, spawn_point)
            except RuntimeError:
                continue
            controller = self.world.spawn_actor(walker_controller_bp, carla.Transform(), attach_to=walker)
            controller.start()
            controller.go_to_location(self.world.get_random_location_from_navigation())
            controller.set_max_speed(1.4)
            self.actors.append(controller)
            self.actors.append(walker)
