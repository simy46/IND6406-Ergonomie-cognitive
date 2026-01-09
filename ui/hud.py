import pygame


PANEL_BG = (15, 15, 18, 200)
PANEL_BORDER = (0, 180, 220)
TEXT_COLOR = (235, 235, 235)
MUTED_TEXT = (170, 170, 170)
SPEED_COLOR = (0, 220, 255)


def _draw_panel(screen, rect, border_color=PANEL_BORDER, fill_color=PANEL_BG, radius=10):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    panel.fill((0, 0, 0, 0))
    pygame.draw.rect(panel, fill_color, panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, border_color, panel.get_rect(), 2, border_radius=radius)
    screen.blit(panel, rect.topleft)


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
    font = pygame.font.SysFont(None, 24)
    font_small = pygame.font.SysFont(None, 20)
    font_speed = pygame.font.SysFont(None, 64)
    font_speed_unit = pygame.font.SysFont(None, 24)
    x = 20
    y = 20
    line_gap = 22

    panel_rect = pygame.Rect(x, y, 360, 260)
    _draw_panel(screen, panel_rect)
    content_x = panel_rect.x + 16
    content_y = panel_rect.y + 14

    elapsed = telemetry.get_mission_elapsed_seconds()
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    timer_text = f"{minutes:02d}:{seconds:02d}"
    lines = [
        f"Student: {telemetry.student_name}",
        f"Mode: {telemetry.selected_mode}",
        f"Drive mode: {active_drive_mode}",
        f"Timer: {timer_text}",
        f"Distance: {telemetry.distance_traveled_meters:.1f} m",
        f"In lane (%): {telemetry.get_percent_in_lane():.1f}",
        f"Lane offset (avg): {telemetry.get_lane_offset_mean():.2f} m",
        f"Lane invasions: {telemetry.lane_invasion_count}",
        f"Collisions: {telemetry.collision_count}",
        f"Manual time: {telemetry.manual_time_seconds:.1f}s",
        f"Auto time: {telemetry.auto_time_seconds:.1f}s",
    ]
    for line in lines:
        screen.blit(font.render(line, True, TEXT_COLOR), (content_x, content_y))
        content_y += line_gap

    speed_rect = pygame.Rect(x, panel_rect.bottom + 14, 360, 120)
    _draw_panel(screen, speed_rect)
    speed_value = f"{telemetry.current_speed_kmh:.0f}"
    speed_label = "KM/H"
    label_text = font_small.render("SPEED", True, MUTED_TEXT)
    screen.blit(label_text, (speed_rect.x + 16, speed_rect.y + 10))
    speed_text = font_speed.render(speed_value, True, SPEED_COLOR)
    speed_text_rect = speed_text.get_rect()
    speed_text_rect.midleft = (speed_rect.x + 20, speed_rect.y + 70)
    screen.blit(speed_text, speed_text_rect)
    unit_text = font_speed_unit.render(speed_label, True, TEXT_COLOR)
    unit_rect = unit_text.get_rect()
    unit_rect.bottomleft = (speed_text_rect.right + 10, speed_rect.y + 100)
    screen.blit(unit_text, unit_rect)
    if telemetry.selected_mode == "takeover":
        requested = "YES" if telemetry.takeover_requested else "NO"
        reaction = telemetry.get_takeover_reaction_time()
        reaction_text = "N/A"
        if reaction is not None:
            reaction_text = f"{reaction:.2f}s"
        takeover_line = f"Takeover requested: {requested}"
        screen.blit(font_small.render(takeover_line, True, TEXT_COLOR), (content_x, content_y))
        content_y += line_gap
        reaction_line = f"Reaction time: {reaction_text}"
        screen.blit(font_small.render(reaction_line, True, TEXT_COLOR), (content_x, content_y))
