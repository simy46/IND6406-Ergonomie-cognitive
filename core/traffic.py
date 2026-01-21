import random

import carla

from core.traffic_spawn import spawn_vehicles, spawn_walkers


class TrafficController:
    def __init__(
        self,
        client,
        world,
        vehicle_count,
        walker_count,
        min_distance_from_ego,
        min_distance_from_route,
    ):
        self.client = client
        self.world = world
        self.vehicle_count = int(vehicle_count)
        self.walker_count = int(walker_count)
        self.min_distance_from_ego = float(min_distance_from_ego)
        self.min_distance_from_route = float(min_distance_from_route)
        self.actors = []

    def apply(self, enabled, reference_location=None, avoid_locations=None, avoid_road_ids=None):
        if enabled:
            if not self.actors:
                self._spawn_traffic(reference_location, avoid_locations, avoid_road_ids)
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

    def _spawn_traffic(self, reference_location=None, avoid_locations=None, avoid_road_ids=None):
        self.destroy_all()
        spawn_points = self.world.get_map().get_spawn_points()
        if reference_location is not None:
            spawn_points = [
                sp for sp in spawn_points
                if sp.location.distance(reference_location) >= self.min_distance_from_ego
            ]
        if avoid_locations:
            filtered = []
            for sp in spawn_points:
                keep = True
                for loc in avoid_locations:
                    if sp.location.distance(loc) < self.min_distance_from_route:
                        keep = False
                        break
                if keep:
                    filtered.append(sp)
            spawn_points = filtered
        if avoid_road_ids:
            filtered = []
            carla_map = self.world.get_map()
            for sp in spawn_points:
                waypoint = carla_map.get_waypoint(
                    sp.location,
                    project_to_road=True,
                    lane_type=carla.LaneType.Driving,
                )
                if waypoint is None or waypoint.road_id in avoid_road_ids:
                    continue
                filtered.append(sp)
            spawn_points = filtered
        if not spawn_points:
            print("[TRAFFIC][WARN] No spawn points after filtering; traffic disabled.")
            return
        random.shuffle(spawn_points)

        traffic_manager = self.client.get_trafficmanager()
        sync_enabled = self.world.get_settings().synchronous_mode
        traffic_manager.set_synchronous_mode(sync_enabled)
        traffic_manager.set_global_distance_to_leading_vehicle(3.0)

        actors = spawn_vehicles(
            self.client,
            self.world,
            traffic_manager,
            spawn_points,
            self.vehicle_count,
        )
        self.actors.extend(actors)
        if sync_enabled:
            self.world.tick()

        actors = spawn_walkers(self.client, self.world, self.walker_count)
        self.actors.extend(actors)
        if sync_enabled:
            self.world.tick()
