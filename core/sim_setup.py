import time

import carla

from core.mission import pick_start_and_destination
from core.mission_manager import MissionManager
from core.pause import PauseController
from core.camera import CameraRGB
from core.sim_utils import connect_world
from input.steering_wheel import SteeringWheel


def setup_world(client, sync_enabled=True):
    world = connect_world(client, attempts=6, delay=2.0, do_reload=True)
    original_settings = world.get_settings()
    traffic_manager = None
    if sync_enabled:
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 1.0 / 60.0
        world.apply_settings(settings)
        traffic_manager = client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)
    return world, original_settings, sync_enabled, traffic_manager


def spawn_vehicle(world):
    blueprint = world.get_blueprint_library().find("vehicle.tesla.model3")
    vehicle = world.spawn_actor(blueprint, pick_start_and_destination(world)[0])
    vehicle.apply_control(carla.VehicleControl())
    time.sleep(0.5)
    return vehicle


def setup_runtime(client, world, vehicle):
    camera = CameraRGB(world, vehicle)
    wheel = SteeringWheel(debug=True)
    mission_manager = MissionManager(client, world, vehicle, wheel)
    pause_controller = PauseController(vehicle)
    return camera, wheel, mission_manager, pause_controller
