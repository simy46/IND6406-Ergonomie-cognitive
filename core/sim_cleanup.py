from core.sim_utils import cleanup_world_actors, safe_destroy


def cleanup_simulation(
    mission_manager,
    camera,
    vehicle,
    world,
    sync_enabled,
    original_settings,
    traffic_manager,
):
    try:
        if mission_manager is not None:
            mission_manager.traffic_controller.destroy_all()
            if mission_manager.telemetry is not None:
                mission_manager.telemetry.cleanup()
    except Exception:
        pass
    safe_destroy(camera)
    safe_destroy(vehicle)
    cleanup_world_actors(world)
    if sync_enabled:
        try:
            world.apply_settings(original_settings)
        except Exception:
            pass
    if traffic_manager is not None:
        try:
            traffic_manager.set_synchronous_mode(False)
        except Exception:
            pass
