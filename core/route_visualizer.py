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
    start = location + carla.Location(z=3.0)
    end = location + carla.Location(z=0.4)
    world.debug.draw_arrow(
        start,
        end,
        thickness=0.08,
        arrow_size=0.28,
        color=carla.Color(235, 235, 235),
        life_time=life_time
    )


