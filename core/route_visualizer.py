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
    end = location + carla.Location(z=0.6)
    color = carla.Color(220, 220, 220)
    world.debug.draw_line(
        start,
        end,
        thickness=0.05,
        color=color,
        life_time=life_time
    )
    left = end + carla.Location(x=-0.25, z=0.25)
    right = end + carla.Location(x=0.25, z=0.25)
    world.debug.draw_line(
        left,
        end,
        thickness=0.05,
        color=color,
        life_time=life_time
    )
    world.debug.draw_line(
        right,
        end,
        thickness=0.05,
        color=color,
        life_time=life_time
    )


