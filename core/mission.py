import random
import carla

from agents.navigation.global_route_planner import GlobalRoutePlanner
from core.constants import (
    ROUTE_MIN_METERS,
    ROUTE_MAX_METERS,
    ROUTE_ATTEMPTS,
    ROUTE_MAX_TOTAL_ATTEMPTS,
    ROUTE_MIN_SECONDS,
    ROUTE_SPEED_KMH,
    ROUTE_STRICT_MIN,
)


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


def compute_route_length(route):
    if not route:
        return 0.0
    total = 0.0
    prev = None
    for wp, _ in route:
        loc = wp.transform.location
        if prev is not None:
            total += prev.distance(loc)
        prev = loc
    return total


def pick_long_route(world):
    spawn_points = world.get_map().get_spawn_points()
    best = None
    best_length = 0.0
    min_speed_ms = max(0.1, ROUTE_SPEED_KMH / 3.6)
    min_length = max(ROUTE_MIN_METERS, min_speed_ms * ROUTE_MIN_SECONDS)
    total_attempts = 0
    while total_attempts < ROUTE_MAX_TOTAL_ATTEMPTS:
        for _ in range(ROUTE_ATTEMPTS):
            total_attempts += 1
            start = random.choice(spawn_points)
            dest = random.choice(spawn_points)
            while start.location.distance(dest.location) < 50:
                dest = random.choice(spawn_points)
            route = compute_route(world, start.location, dest.location)
            length = compute_route_length(route)
            if min_length <= length <= ROUTE_MAX_METERS:
                return start, dest, route
            if length > best_length:
                best = (start, dest, route)
                best_length = length
        if total_attempts >= ROUTE_MAX_TOTAL_ATTEMPTS:
            if ROUTE_STRICT_MIN:
                print("[ROUTE] Trajet long non trouve, nouveau cycle.")
            break
    if best is not None:
        return best
    start, dest = pick_start_and_destination(world)
    route = compute_route(world, start.location, dest.location)
    return start, dest, route

def reached_destination(vehicle, destination, threshold=5.0):
    return vehicle.get_location().distance(destination.location) < threshold


from core.constants import DRIVE_AUTOMATIC, DRIVE_MANUAL


def toggle_manual_auto(active_drive_mode, ensure_autonomous_driver, takeover_controller):
    if active_drive_mode == DRIVE_AUTOMATIC:
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

        active_drive_mode = DRIVE_AUTOMATIC
        print("[MODE] Switched to AUTO")

    return active_drive_mode
