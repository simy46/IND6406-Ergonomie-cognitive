from core.constants import NBACK_RESPONSE_BUTTON


def run_mission_step(mission_manager, wheel, dt):
    mission_manager.run_mission_mode()
    nback_click = False
    if mission_manager.mission_active:
        try:
            nback_click = wheel.was_button_pressed(NBACK_RESPONSE_BUTTON)
        except Exception:
            nback_click = False
    mission_manager.update_telemetry(dt, nback_click=nback_click)
    mission_manager.prepare_next_route()
