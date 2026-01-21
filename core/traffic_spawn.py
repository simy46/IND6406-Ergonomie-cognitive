import random

import carla


def spawn_vehicles(client, world, traffic_manager, spawn_points, vehicle_count):
    blueprint_library = world.get_blueprint_library()
    vehicle_bps = blueprint_library.filter("vehicle.*")
    batch = []
    vehicle_count = min(int(vehicle_count), len(spawn_points))
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
    try:
        results = client.apply_batch_sync(batch, True)
    except Exception as e:
        print(f"[TRAFFIC][ERROR] Vehicle spawn batch failed: {e}")
        return []
    actors = []
    for result in results:
        if result.error:
            print(f"[TRAFFIC][WARN] Vehicle spawn failed: {result.error}")
            continue
        actor = world.get_actor(result.actor_id)
        if actor is not None:
            try:
                traffic_manager.auto_lane_change(actor, False)
                traffic_manager.vehicle_percentage_speed_difference(actor, 10)
            except Exception:
                pass
            actors.append(actor)
    if vehicle_count > 0:
        print(f"[TRAFFIC] Vehicles spawned: {len(actors)}/{vehicle_count}")
    return actors


def spawn_walkers(client, world, walker_count):
    if int(walker_count) <= 0:
        return []
    blueprint_library = world.get_blueprint_library()
    walker_bps = blueprint_library.filter("walker.pedestrian.*")
    walker_controller_bp = blueprint_library.find("controller.ai.walker")
    walker_transforms = []
    for _ in range(int(walker_count)):
        location = world.get_random_location_from_navigation()
        if location:
            walker_transforms.append(carla.Transform(location))

    walker_batch = []
    for transform in walker_transforms:
        bp = random.choice(walker_bps)
        walker_batch.append(carla.command.SpawnActor(bp, transform))
    try:
        walker_results = client.apply_batch_sync(walker_batch, True)
    except Exception as e:
        print(f"[TRAFFIC][ERROR] Walker spawn batch failed: {e}")
        return []
    walker_ids = [r.actor_id for r in walker_results if not r.error]

    controller_batch = []
    for walker_id in walker_ids:
        controller_batch.append(
            carla.command.SpawnActor(walker_controller_bp, carla.Transform(), walker_id)
        )
    try:
        controller_results = client.apply_batch_sync(controller_batch, True)
    except Exception as e:
        print(f"[TRAFFIC][ERROR] Walker controller spawn failed: {e}")
        return []
    controller_ids = [r.actor_id for r in controller_results if not r.error]

    actors = []
    for controller_id, walker_id in zip(controller_ids, walker_ids):
        controller = world.get_actor(controller_id)
        walker = world.get_actor(walker_id)
        if controller is None or walker is None:
            continue
        controller.start()
        controller.go_to_location(world.get_random_location_from_navigation())
        controller.set_max_speed(1.4)
        actors.append(controller)
        actors.append(walker)
    if walker_count > 0:
        print(f"[TRAFFIC] Walkers spawned: {len(walker_ids)}/{walker_count}")
    return actors
