import random
import carla


class TrafficController:
    def __init__(self, client, world, vehicle_count, walker_count, min_distance_from_ego):
        self.client = client
        self.world = world
        self.vehicle_count = int(vehicle_count)
        self.walker_count = int(walker_count)
        self.min_distance_from_ego = float(min_distance_from_ego)
        self.actors = []

    def apply(self, enabled, reference_location=None):
        if enabled:
            if not self.actors:
                self._spawn_traffic(reference_location)
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

    def _spawn_traffic(self, reference_location=None):
        self.destroy_all()
        blueprint_library = self.world.get_blueprint_library()
        spawn_points = self.world.get_map().get_spawn_points()
        if reference_location is not None:
            spawn_points = [
                sp for sp in spawn_points
                if sp.location.distance(reference_location) >= self.min_distance_from_ego
            ]
        random.shuffle(spawn_points)

        traffic_manager = self.client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(False)
        traffic_manager.set_global_distance_to_leading_vehicle(3.0)

        vehicle_bps = blueprint_library.filter("vehicle.*")
        vehicle_count = min(self.vehicle_count, len(spawn_points))
        batch = []
        for spawn_point in spawn_points[:vehicle_count]:
            bp = random.choice(vehicle_bps)
            if bp.has_attribute("color"):
                color = random.choice(bp.get_attribute("color").recommended_values)
                bp.set_attribute("color", color)
            batch.append(
                carla.command.SpawnActor(bp, spawn_point).then(
                    carla.command.SetAutopilot(
                        carla.command.FutureActor, True, traffic_manager.get_port()
                    )
                )
            )
        results = self.client.apply_batch_sync(batch, True)
        for result in results:
            if result.error:
                print(f"[TRAFFIC][WARN] Vehicle spawn failed: {result.error}")
                continue
            actor = self.world.get_actor(result.actor_id)
            if actor is not None:
                try:
                    traffic_manager.auto_lane_change(actor, False)
                    traffic_manager.vehicle_percentage_speed_difference(actor, 10)
                except Exception:
                    pass
                self.actors.append(actor)

        walker_bps = blueprint_library.filter("walker.pedestrian.*")
        walker_controller_bp = blueprint_library.find("controller.ai.walker")
        walker_transforms = []
        for _ in range(self.walker_count):
            location = self.world.get_random_location_from_navigation()
            if location:
                walker_transforms.append(carla.Transform(location))

        walker_batch = []
        for transform in walker_transforms:
            bp = random.choice(walker_bps)
            walker_batch.append(carla.command.SpawnActor(bp, transform))
        walker_results = self.client.apply_batch_sync(walker_batch, True)
        walker_ids = [r.actor_id for r in walker_results if not r.error]

        controller_batch = []
        for walker_id in walker_ids:
            controller_batch.append(
                carla.command.SpawnActor(walker_controller_bp, carla.Transform(), walker_id)
            )
        controller_results = self.client.apply_batch_sync(controller_batch, True)
        controller_ids = [r.actor_id for r in controller_results if not r.error]

        for controller_id, walker_id in zip(controller_ids, walker_ids):
            controller = self.world.get_actor(controller_id)
            walker = self.world.get_actor(walker_id)
            if controller is None or walker is None:
                continue
            controller.start()
            controller.go_to_location(self.world.get_random_location_from_navigation())
            controller.set_max_speed(1.4)
            self.actors.append(controller)
            self.actors.append(walker)
