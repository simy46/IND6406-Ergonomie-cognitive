import random
import carla

from agents.navigation.global_route_planner import GlobalRoutePlanner
from core.constants import CHAIN_MIN_DISTANCE_METERS


def pick_start_and_destination(world):
    """
    Pick two valid spawn points far enough from each other
    """
    spawn_points = world.get_map().get_spawn_points()

    start = random.choice(spawn_points)
    dest = random.choice(spawn_points)

    while start.location.distance(dest.location) < 50:
        dest = random.choice(spawn_points)

    return start, dest


def compute_route(world, start_location, destination_location, resolution=2.0):
    """
    Compute a global route using CARLA GlobalRoutePlanner
    """
    carla_map = world.get_map()

    grp = GlobalRoutePlanner(carla_map, resolution)
    route = grp.trace_route(start_location, destination_location)

    return route


def pick_destination_far(world, from_location):
    spawn_points = world.get_map().get_spawn_points()
    dest = random.choice(spawn_points)
    while from_location.distance(dest.location) < CHAIN_MIN_DISTANCE_METERS:
        dest = random.choice(spawn_points)
    return dest

def reached_destination(vehicle, destination, threshold=5.0):
    return vehicle.get_location().distance(destination.location) < threshold


from core.constants import DRIVE_AUTONOMOUS, DRIVE_MANUAL


def toggle_manual_auto(active_drive_mode, ensure_autonomous_driver, takeover_controller):
    if active_drive_mode == DRIVE_AUTONOMOUS:
        if takeover_controller:
            takeover_controller.play_noa_disabled()

        active_drive_mode = DRIVE_MANUAL
        print("[MODE] Switched to MANUAL")

        if takeover_controller:
            takeover_controller.mark_manual_override(reason="ESC")

    else:
        ensure_autonomous_driver()
        if takeover_controller:
            takeover_controller.play_noa_enabled()

        active_drive_mode = DRIVE_AUTONOMOUS
        print("[MODE] Switched to AUTO")

    return active_drive_mode
