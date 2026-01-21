from ui.hud import draw_center_message, render_hud
from ui.nback import render_nback


def render_frame(screen, camera, mission_manager, hud_visible):
    screen.fill((0, 0, 0))
    camera.render(screen)
    render_hud(
        screen,
        mission_manager.telemetry,
        mission_manager.active_drive_mode,
        hud_visible=hud_visible,
    )
    if mission_manager.mission_active:
        elapsed = None
        if mission_manager.telemetry is not None:
            elapsed = mission_manager.telemetry.get_mission_elapsed_seconds()
        render_nback(screen, mission_manager.nback_task, elapsed)

    if mission_manager.show_restart_prompt:
        hud_visible = True
        draw_center_message(
            screen,
            "Mission terminée: Appuyez sur [ESPACE]",
            color=(0, 220, 255),
        )
    return hud_visible
