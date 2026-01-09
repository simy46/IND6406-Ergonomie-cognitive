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
    world.debug.draw_point(
        location + carla.Location(z=1.0),
        size=0.3,
        color=carla.Color(255, 80, 80),
        life_time=life_time
    )


