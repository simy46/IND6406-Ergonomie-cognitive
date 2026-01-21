from core.constants import (
    DRIVE_MANUAL,
    DRIVE_AUTONOMOUS,
    MODE_TAKEOVER,
)
from core.mission import toggle_manual_auto
from scenarios.scenario_autonomous import AutonomousDriver
from scenarios.scenario_manual import run_manual_mode
from scenarios.scenario_takeover import TakeoverController


class MissionManagerDriveMixin:
    def ensure_autonomous_driver(self):
        if self.autonomous_driver is None:
            self.autonomous_driver = AutonomousDriver(self.vehicle, self.route)

    def handle_escape(self):
        if self.selected_mode == MODE_TAKEOVER and self.takeover_controller is not None:
            self.active_drive_mode = self.takeover_controller.toggle_mode(self.active_drive_mode)
        else:
            self.active_drive_mode = toggle_manual_auto(
                self.active_drive_mode,
                self.ensure_autonomous_driver,
                self.takeover_controller,
            )
        if self.telemetry is not None:
            self.telemetry.record_mode_switch()

    def run_mission_mode(self):
        if not self.mission_active:
            return
        if self.selected_mode == MODE_TAKEOVER and self.takeover_controller is not None:
            if self.active_drive_mode == DRIVE_AUTONOMOUS:
                self.takeover_controller.update_auto_only()
            else:
                if self.takeover_controller.detect_human_input():
                    self.takeover_controller.mark_manual_override(reason="human_input")
                run_manual_mode(self.context)
        else:
            if self.active_drive_mode == DRIVE_MANUAL:
                run_manual_mode(self.context)
            elif self.active_drive_mode == DRIVE_AUTONOMOUS:
                self.ensure_autonomous_driver()
                self.autonomous_driver.run_step()

    def _rebuild_autonomy(self):
        if self.selected_mode == MODE_TAKEOVER:
            if self.takeover_controller is not None:
                self.takeover_controller.auto = AutonomousDriver(self.vehicle, self.route)
                self.autonomous_driver = self.takeover_controller.auto
            else:
                self.ensure_autonomous_driver()
                self.takeover_controller = TakeoverController(
                    self.vehicle,
                    self.autonomous_driver,
                    self.wheel,
                )
