from core.constants import (
    CHAIN_ENABLED,
    CHAIN_MIN_SECONDS,
    CHAIN_PREVIEW_DISTANCE_METERS,
    DRIVE_AUTOMATIC,
)
from core.mission import compute_route, pick_destination_far, reached_destination


class MissionManagerRoutesMixin:
    def mission_is_done(self):
        if self.active_drive_mode == DRIVE_AUTOMATIC and self.autonomous_driver is not None:
            return self.autonomous_driver.is_done()
        return reached_destination(self.vehicle, self.destination)

    def freeze_vehicle_end(self):
        from carla import VehicleControl

        self.vehicle.apply_control(
            VehicleControl(
                throttle=0.0,
                brake=1.0,
                steer=0.0,
                hand_brake=True,
                reverse=False,
            )
        )

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
            new_dest.location,
        )
        self.next_destination = new_dest
        self.next_route = new_route
        print("[MISSION] Nouveau trajet precharge")

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
                            new_dest.location,
                        )
                        self.destination = new_dest
                        self.route = new_route
                    self.next_route = None
                    self.next_destination = None
                    self.autonomous_driver = None
                    self._rebuild_autonomy()
                    self.telemetry.update_route(self.route, self.destination, self.takeover_controller)
                    self.last_debug_draw = 0.0
                    print("[MISSION] Nouveau trajet: durée minimale non atteinte")
                    return
            self.mission_active = False
            self.show_restart_prompt = True
            self.freeze_vehicle_end()
            if self.telemetry is not None:
                metrics = self.telemetry.finalize()
                from core.logger import append_row

                append_row(metrics)
                self.telemetry.cleanup()
                self.telemetry.pause()
            print(f"[MISSION] Completed by {self.student_name}")
