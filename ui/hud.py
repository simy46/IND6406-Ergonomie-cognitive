import pygame


def draw_hud_message(
    screen,
    text,
    position=(200, 30),
    color=(0, 220, 255),
    font_size=36
):
    font = pygame.font.SysFont(None, font_size)
    msg = font.render(text, True, color)
    screen.blit(msg, position)


def render_hud(screen, telemetry, active_drive_mode):
    if telemetry is None:
        return
    font = pygame.font.SysFont(None, 26)
    y = 20
    x = 20
    line_gap = 24
    elapsed = telemetry.get_mission_elapsed_seconds()
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    timer_text = f"{minutes:02d}:{seconds:02d}"
    lines = [
        f"Student: {telemetry.student_name}",
        f"Mode: {telemetry.selected_mode}",
        f"Drive mode: {active_drive_mode}",
        f"Timer: {timer_text}",
        f"Speed: {telemetry.current_speed_kmh:.1f} km/h",
        f"Distance: {telemetry.distance_traveled_meters:.1f} m",
        f"In lane (%): {telemetry.get_percent_in_lane():.1f}",
        f"Lane offset (avg): {telemetry.get_lane_offset_mean():.2f} m",
        f"Lane invasions: {telemetry.lane_invasion_count}",
        f"Collisions: {telemetry.collision_count}",
        f"Manual time: {telemetry.manual_time_seconds:.1f}s",
        f"Auto time: {telemetry.auto_time_seconds:.1f}s",
    ]
    for line in lines:
        screen.blit(font.render(line, True, (255, 255, 255)), (x, y))
        y += line_gap
    if telemetry.selected_mode == "takeover":
        requested = "YES" if telemetry.takeover_requested else "NO"
        reaction = telemetry.get_takeover_reaction_time()
        reaction_text = "N/A"
        if reaction is not None:
            reaction_text = f"{reaction:.2f}s"
        takeover_line = f"Takeover requested: {requested}"
        screen.blit(font.render(takeover_line, True, (255, 255, 255)), (x, y))
        y += line_gap
        reaction_line = f"Reaction time: {reaction_text}"
        screen.blit(font.render(reaction_line, True, (255, 255, 255)), (x, y))
