import time

from core.constants import DRIVE_AUTONOMOUS, DRIVE_MANUAL


def update_auto_only(controller):
    controller.auto.run_step()


def toggle_mode(controller, active_drive_mode):
    now = time.time()
    if active_drive_mode == DRIVE_AUTONOMOUS:
        controller.takeover_requested = True
        controller.request_time = now
        controller.takeover_done = False
        controller.manual_override = False
        controller.play_noa_disabled()
        print("[TAKEOVER] Switching to MANUAL (requested)")
        return DRIVE_MANUAL
    controller.play_noa_enabled()
    print("[TAKEOVER] Switching to AUTO")
    return DRIVE_AUTONOMOUS


def detect_human_input(controller, steer_eps=0.05, pedal_eps=0.05) -> bool:
    if not controller.wheel:
        return False
    control = controller.wheel.get_control()
    return (
        abs(control.steer) > steer_eps
        or control.throttle > pedal_eps
        or control.brake > pedal_eps
    )


def mark_manual_override(controller, reason="human"):
    now = time.time()
    if controller.takeover_requested and controller.request_time is not None:
        if controller.reaction_time is None:
            controller.reaction_time = now - controller.request_time
            controller.takeover_done = True
            print(f"[TAKEOVER] Repris en {controller.reaction_time:.2f}s ({reason})")
    else:
        controller.manual_override = True
        print(f"[TAKEOVER] Manual override ({reason})")
