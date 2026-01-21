import time


def cleanup_world_actors(world):
    for pattern in ("vehicle.*", "walker.pedestrian.*", "controller.ai.walker", "sensor.*"):
        for actor in world.get_actors().filter(pattern):
            try:
                actor.destroy()
            except Exception:
                pass


def safe_destroy(actor):
    if actor is None:
        return
    try:
        actor.destroy()
    except Exception:
        pass


def connect_world(client, attempts=5, delay=2.0, do_reload=True):
    last_err = None
    for attempt in range(1, attempts + 1):
        try:
            world = client.get_world()
            if do_reload:
                try:
                    world = client.reload_world()
                except RuntimeError as e:
                    print(f"[WARN] reload_world failed: {e}")
                    world = client.get_world()
            return world
        except RuntimeError as e:
            last_err = e
            print(f"[WARN] connect attempt {attempt}/{attempts} failed: {e}")
            time.sleep(delay)
    raise last_err
