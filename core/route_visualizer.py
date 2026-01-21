import carla


def draw_route(world, route, life_time=1.1):
    for wp, _ in route:
        start = wp.transform.location + carla.Location(z=0.35)
        forward = wp.transform.get_forward_vector()
        right = wp.transform.get_right_vector()
        end = start + carla.Location(
            x=forward.x * 0.6,
            y=forward.y * 0.6,
            z=forward.z * 0.1,
        )
        color = carla.Color(60, 90, 120)
        world.debug.draw_line(
            start,
            end,
            thickness=0.03,
            color=color,
            life_time=life_time,
        )
        head_left = end - carla.Location(
            x=forward.x * 0.12 - right.x * 0.07,
            y=forward.y * 0.12 - right.y * 0.07,
            z=0.0,
        )
        head_right = end - carla.Location(
            x=forward.x * 0.12 + right.x * 0.07,
            y=forward.y * 0.12 + right.y * 0.07,
            z=0.0,
        )
        world.debug.draw_line(
            end,
            head_left,
            thickness=0.03,
            color=color,
            life_time=life_time,
        )
        world.debug.draw_line(
            end,
            head_right,
            thickness=0.03,
            color=color,
            life_time=life_time,
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


