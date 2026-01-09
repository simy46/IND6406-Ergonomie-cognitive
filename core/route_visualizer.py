import carla


def draw_route(world, route, life_time=1.1):
    for wp, _ in route:
        world.debug.draw_point(
            wp.transform.location + carla.Location(z=0.3),
            size=0.07,
            color=carla.Color(0, 150, 255),
            life_time=life_time
        )


def draw_destination(world, location, life_time=1.1):
    waypoint = world.get_map().get_waypoint(
        location,
        project_to_road=True,
        lane_type=carla.LaneType.Driving,
    )
    forward = carla.Vector3D(1.0, 0.0, 0.0)
    if waypoint is not None:
        forward = waypoint.transform.get_forward_vector()
    start = location + carla.Location(z=0.2)
    end = start + carla.Location(
        x=forward.x * 2.0,
        y=forward.y * 2.0,
        z=0.2,
    )
    world.debug.draw_arrow(
        start,
        end,
        thickness=0.12,
        arrow_size=0.35,
        color=carla.Color(255, 120, 120),
        life_time=life_time
    )


