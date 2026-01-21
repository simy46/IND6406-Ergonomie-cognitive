import carla

from core.constants import (
    TRAFFIC_VEHICLES,
    TRAFFIC_PEDESTRIANS,
    TRAFFIC_MIN_DISTANCE_FROM_EGO,
    TRAFFIC_MIN_DISTANCE_FROM_ROUTE,
)
from core.traffic import TrafficController
from core.telemetry import Telemetry


class MissionManagerBase:
    def __init__(self, client, world, vehicle, wheel):
        self.world = world
        self.client = client
        self.vehicle = vehicle
        self.wheel = wheel
        self.context = {"vehicle": vehicle, "wheel": wheel}
        self.in_menu = True
        self.mission_active = False
        self.show_restart_prompt = False
        self.student_name = None
        self.selected_mode = None
        self.active_drive_mode = None
        self.autonomous_driver = None
        self.takeover_controller = None
        self.start = None
        self.destination = None
        self.route = None
        self.next_route = None
        self.next_destination = None
        self.last_debug_draw = 0.0
        self.telemetry = None
        self.nback_task = None
        self.traffic_controller = TrafficController(
            client,
            world,
            TRAFFIC_VEHICLES,
            TRAFFIC_PEDESTRIANS,
            TRAFFIC_MIN_DISTANCE_FROM_EGO,
            TRAFFIC_MIN_DISTANCE_FROM_ROUTE,
        )

    def reset_vehicle_to_spawn(self, spawn_transform: carla.Transform):
        self.vehicle.set_transform(spawn_transform)
        self.vehicle.set_target_velocity(carla.Vector3D(0.0, 0.0, 0.0))
        self.vehicle.set_target_angular_velocity(carla.Vector3D(0.0, 0.0, 0.0))
        self.vehicle.apply_control(
            carla.VehicleControl(
                throttle=0.0,
                brake=0.0,
                steer=0.0,
                hand_brake=False,
                reverse=False,
            )
        )

    def reset_state_to_menu(self):
        was_active = self.mission_active
        should_log = was_active and not self.show_restart_prompt
        if should_log and self.telemetry is not None:
            from core.logger import append_row

            metrics = self.telemetry.finalize()
            append_row(metrics)
            self.telemetry.cleanup()
            self.telemetry.pause()
            self.telemetry = None
        self.in_menu = True
        self.mission_active = False
        self.show_restart_prompt = False
        self.autonomous_driver = None
        self.takeover_controller = None
        self.selected_mode = None
        self.active_drive_mode = None
        self.last_debug_draw = 0.0
        self.next_route = None
        self.next_destination = None
        self.nback_task = None
        self.traffic_controller.destroy_all()
        if self.telemetry is not None:
            self.telemetry.cleanup()
            self.telemetry = None
        self.vehicle.apply_control(
            carla.VehicleControl(
                throttle=0.0,
                brake=0.0,
                steer=0.0,
                hand_brake=False,
                reverse=False,
            )
        )
        print("[MISSION] Returning to menu")

    def finalize_if_active(self):
        was_active = self.mission_active
        should_log = was_active and not self.show_restart_prompt
        if should_log and self.telemetry is not None:
            from core.logger import append_row

            metrics = self.telemetry.finalize()
            append_row(metrics)
            self.telemetry.cleanup()
            self.telemetry.pause()
            self.telemetry = None

    def update_telemetry(self, dt, nback_click=False):
        if self.mission_active and self.telemetry is not None:
            self.telemetry.update(self.active_drive_mode, dt, nback_click=nback_click)

    def should_draw_debug(self, now):
        if self.mission_active and (now - self.last_debug_draw) > 1.0:
            self.last_debug_draw = now
            return True
        return False
