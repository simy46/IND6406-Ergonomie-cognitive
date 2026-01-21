from core.constants import (
    MODE_MANUAL,
    MODE_AUTOMATIC,
    MODE_TAKEOVER,
    DRIVE_MANUAL,
    DRIVE_AUTOMATIC,
    TRAFFIC_AVOID_ROUTE_ROADS,
    NBACK_LEVEL,
    NBACK_INTERVAL_SECONDS,
    NBACK_TOTAL_TRIALS,
    NBACK_POSITIONS,
)
from core.mission import pick_start_and_destination, compute_route
from core.nback import SpatialNBackTask
from scenarios.scenario_autonomous import AutonomousDriver
from scenarios.scenario_takeover import TakeoverController
from ui.mission_menu import mission_popup


class MissionManagerMenuMixin:
    def run_menu(self, screen, clock):
        if not self.in_menu:
            return True
        result = mission_popup(screen, clock)
        if not result or result[0] is None:
            return False
        self.student_name, self.selected_mode, traffic_enabled, nback_config, nback_enabled = result
        if not self.student_name:
            return False
        self.start, self.destination = pick_start_and_destination(self.world)
        self.route = compute_route(self.world, self.start.location, self.destination.location)
        self.next_route = None
        self.next_destination = None
        self.nback_task = None
        if nback_enabled:
            nback_level = NBACK_LEVEL
            nback_interval = NBACK_INTERVAL_SECONDS
            nback_rounds = NBACK_TOTAL_TRIALS
            if nback_config:
                nback_level = nback_config.get("level", nback_level)
                nback_interval = nback_config.get("interval", nback_interval)
                rounds = nback_config.get("rounds", nback_rounds)
                if rounds is None:
                    nback_rounds = 10**9
                else:
                    nback_rounds = rounds
            self.nback_task = SpatialNBackTask(
                level=nback_level,
                interval_seconds=nback_interval,
                total_trials=nback_rounds,
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
            self.takeover_controller = TakeoverController(
                self.vehicle, self.autonomous_driver, self.wheel
            )
            self.active_drive_mode = DRIVE_AUTOMATIC
        self.telemetry = self._create_telemetry()
        self.mission_active = True
        self.in_menu = False
        self.show_restart_prompt = False
        self.last_debug_draw = 0.0
        self.next_route = None
        self.next_destination = None
        print(f"[MISSION] Student={self.student_name} | selected_mode={self.selected_mode}")
        return True

    def _create_telemetry(self):
        from core.telemetry import Telemetry

        return Telemetry(
            self.world,
            self.vehicle,
            self.student_name,
            self.selected_mode,
            self.route,
            self.destination,
            self.takeover_controller,
            self.nback_task,
        )
