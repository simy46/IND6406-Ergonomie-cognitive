import carla
from core.mission import (
    compute_route,
    pick_destination_far,
    pick_start_and_destination,
    reached_destination,
    toggle_manual_auto,
)
from core.constants import (
    MODE_MANUAL,
    MODE_AUTOMATIC,
    MODE_TAKEOVER,
    DRIVE_MANUAL,
    DRIVE_AUTOMATIC,
    TRAFFIC_VEHICLES,
    TRAFFIC_PEDESTRIANS,
    TRAFFIC_MIN_DISTANCE_FROM_EGO,
    TRAFFIC_MIN_DISTANCE_FROM_ROUTE,
    TRAFFIC_AVOID_ROUTE_ROADS,
    CHAIN_ENABLED,
    CHAIN_MIN_SECONDS,
    CHAIN_PREVIEW_DISTANCE_METERS,
    NBACK_LEVEL,
    NBACK_INTERVAL_SECONDS,
    NBACK_TOTAL_TRIALS,
    NBACK_POSITIONS,
)
from core.nback import SpatialNBackTask
from core.traffic import TrafficController
from core.telemetry import Telemetry
from core.logger import append_row
from scenarios.scenario_autonomous import AutonomousDriver
from scenarios.scenario_manual import run_manual_mode
from scenarios.scenario_takeover import TakeoverController
from ui.mission_menu import mission_popup
class MissionManager:
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
    def ensure_autonomous_driver(self):
        if self.autonomous_driver is None:
            self.autonomous_driver = AutonomousDriver(self.vehicle, self.route)

    def handle_escape(self):
        self.active_drive_mode = toggle_manual_auto(
            self.active_drive_mode,
            self.ensure_autonomous_driver,
            self.takeover_controller,
        )
        if self.telemetry is not None:
            self.telemetry.record_mode_switch()
    def mission_is_done(self):
        if self.active_drive_mode == DRIVE_AUTOMATIC and self.autonomous_driver is not None:
            return self.autonomous_driver.is_done()
        return reached_destination(self.vehicle, self.destination)

    def freeze_vehicle_end(self):
        self.vehicle.apply_control(
            carla.VehicleControl(
                throttle=0.0,
                brake=1.0,
                steer=0.0,
                hand_brake=True,
                reverse=False,
            )
        )

    def reset_state_to_menu(self):
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

    def run_menu(self, screen, clock):
        if not self.in_menu:
            return True
        self.student_name, self.selected_mode, traffic_enabled = mission_popup(screen, clock)
        if not self.student_name:
            return False
        self.start, self.destination = pick_start_and_destination(self.world)
        self.route = compute_route(self.world, self.start.location, self.destination.location)
        self.next_route = None
        self.next_destination = None
        self.nback_task = SpatialNBackTask(
            level=NBACK_LEVEL,
            interval_seconds=NBACK_INTERVAL_SECONDS,
            total_trials=NBACK_TOTAL_TRIALS,
            positions=NBACK_POSITIONS,
        )
        self.reset_vehicle_to_spawn(self.start)
        avoid_locations = [wp.transform.location for wp, _ in self.route]
        avoid_road_ids = None
        if TRAFFIC_AVOID_ROUTE_ROADS:
            avoid_road_ids = {wp.road_id for wp, _ in self.route}
        self.traffic_controller.apply(
            traffic_enabled,
            self.vehicle.get_location(),
            avoid_locations,
            avoid_road_ids,
        )
        self.autonomous_driver = None
        self.takeover_controller = None
        if self.selected_mode == MODE_MANUAL:
            self.active_drive_mode = DRIVE_MANUAL
        elif self.selected_mode == MODE_AUTOMATIC:
            self.ensure_autonomous_driver()
            self.active_drive_mode = DRIVE_AUTOMATIC
        elif self.selected_mode == MODE_TAKEOVER:
            self.ensure_autonomous_driver()
            self.takeover_controller = TakeoverController(self.vehicle, self.autonomous_driver, self.wheel)
            self.active_drive_mode = DRIVE_AUTOMATIC  # commence en auto
        self.telemetry = Telemetry(
            self.world,
            self.vehicle,
            self.student_name,
            self.selected_mode,
            self.route,
            self.destination,
            self.takeover_controller,
            self.nback_task,
        )
        self.mission_active = True
        self.in_menu = False
        self.show_restart_prompt = False
        self.last_debug_draw = 0.0
        self.next_route = None
        self.next_destination = None
        print(f"[MISSION] Student={self.student_name} | selected_mode={self.selected_mode}")
        return True

    def prepare_next_route(self):
        if not CHAIN_ENABLED or self.telemetry is None or self.next_route is not None:
            return
        elapsed = self.telemetry.get_mission_elapsed_seconds()
        if elapsed >= CHAIN_MIN_SECONDS:
            return
        distance = self.vehicle.get_location().distance(self.destination.location)
        if distance > CHAIN_PREVIEW_DISTANCE_METERS:
            return
        new_dest = pick_destination_far(self.world, self.destination.location)
        new_route = compute_route(
            self.world,
            self.destination.location,
            new_dest.location
        )
        self.next_destination = new_dest
        self.next_route = new_route
        print("[MISSION] Nouveau trajet precharge")

    def run_mission_mode(self):
        if not self.mission_active:
            return
        if self.selected_mode == MODE_TAKEOVER and self.takeover_controller is not None:
            if self.takeover_controller.should_request_manual():
                if self.active_drive_mode != DRIVE_MANUAL:
                    self.active_drive_mode = DRIVE_MANUAL
                    print("[TAKEOVER] Switching to MANUAL (requested)")
            if self.active_drive_mode == DRIVE_AUTOMATIC:
                self.takeover_controller.update_auto_only()
            else:
                if self.takeover_controller.detect_human_input():
                    self.takeover_controller.mark_manual_override(reason="human_input")
                run_manual_mode(self.context)
        else:
            if self.active_drive_mode == DRIVE_MANUAL:
                run_manual_mode(self.context)
            elif self.active_drive_mode == DRIVE_AUTOMATIC:
                self.ensure_autonomous_driver()
                self.autonomous_driver.run_step()

    def update_telemetry(self, dt, nback_click=False):
        if self.mission_active and self.telemetry is not None:
            self.telemetry.update(self.active_drive_mode, dt, nback_click=nback_click)

    def should_draw_debug(self, now):
        if self.mission_active and (now - self.last_debug_draw) > 1.0:
            self.last_debug_draw = now
            return True
        return False

    def check_end(self):
        if self.mission_active and self.mission_is_done():
            if CHAIN_ENABLED and self.telemetry is not None:
                elapsed = self.telemetry.get_mission_elapsed_seconds()
                if elapsed < CHAIN_MIN_SECONDS:
                    if self.next_route is not None and self.next_destination is not None:
                        self.destination = self.next_destination
                        self.route = self.next_route
                    else:
                        new_dest = pick_destination_far(self.world, self.destination.location)
                        new_route = compute_route(
                            self.world,
                            self.destination.location,
                            new_dest.location
                        )
                        self.destination = new_dest
                        self.route = new_route
                    self.next_route = None
                    self.next_destination = None
                    self.autonomous_driver = None
                    if self.selected_mode == MODE_AUTOMATIC:
                        self.ensure_autonomous_driver()
                    elif self.selected_mode == MODE_TAKEOVER:
                        if self.takeover_controller is not None:
                            self.takeover_controller.auto = AutonomousDriver(self.vehicle, self.route)
                            self.autonomous_driver = self.takeover_controller.auto
                        else:
                            self.ensure_autonomous_driver()
                            self.takeover_controller = TakeoverController(
                                self.vehicle,
                                self.autonomous_driver,
                                self.wheel
                            )
                    self.telemetry.update_route(self.route, self.destination, self.takeover_controller)
                    self.last_debug_draw = 0.0
                    print("[MISSION] Nouveau trajet: durée minimale non atteinte")
                    return
            self.mission_active = False
            self.show_restart_prompt = True
            self.freeze_vehicle_end()
            if self.telemetry is not None:
                metrics = self.telemetry.finalize()
                append_row(metrics)
                self.telemetry.cleanup()
                self.telemetry.pause()
            print(f"[MISSION] Completed by {self.student_name}")
