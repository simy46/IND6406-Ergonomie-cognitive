import carla


def draw_route(world, route, life_time=1.1):
    for wp, _ in route:
        start = wp.transform.location + carla.Location(z=0.35)
        forward = wp.transform.get_forward_vector()
        end = start + carla.Location(
            x=forward.x * 0.8,
            y=forward.y * 0.8,
            z=forward.z * 0.2,
        )
        world.debug.draw_arrow(
            start,
            end,
            thickness=0.05,
            arrow_size=0.08,
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


