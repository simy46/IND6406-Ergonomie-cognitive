import time


def update_auto_only(controller):
    now = time.time()
    if controller.takeover_done or controller.manual_override:
        return
    controller.auto.run_step()
    if (not controller.takeover_requested) and ((now - controller.start_time) >= controller.takeover_delay):
        controller.takeover_requested = True
        controller.request_time = now
        controller.play_noa_disabled()
        print("[TAKEOVER] Reprise demandée (NOA disabled)")


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
    if controller.takeover_done:
        return
    now = time.time()
    if controller.takeover_requested and controller.request_time is not None:
        if controller.reaction_time is None:
            controller.reaction_time = now - controller.request_time
        controller.takeover_done = True
        print(f"[TAKEOVER] Repris en {controller.reaction_time:.2f}s ({reason})")
    else:
        controller.manual_override = True
        print(f"[TAKEOVER] Manual override ({reason})")
    controller.play_noa_disabled()
