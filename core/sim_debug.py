from core.constants import CHAIN_ENABLED, CHAIN_MIN_SECONDS
from core.route_visualizer import draw_route, draw_destination


def maybe_draw_debug(world, mission_manager, now):
    if not mission_manager.should_draw_debug(now):
        return
    draw_route(world, mission_manager.route)
    draw_destination_marker = True
    draw_next_route = False
    if CHAIN_ENABLED and mission_manager.telemetry is not None:
        elapsed = mission_manager.telemetry.get_mission_elapsed_seconds()
        if elapsed < CHAIN_MIN_SECONDS:
            draw_next_route = mission_manager.next_route is not None
            draw_destination_marker = not draw_next_route
        else:
            draw_next_route = False
            draw_destination_marker = True
    if draw_next_route and mission_manager.next_route is not None:
        draw_route(world, mission_manager.next_route)
    if draw_destination_marker:
        draw_destination(world, mission_manager.destination.location)
