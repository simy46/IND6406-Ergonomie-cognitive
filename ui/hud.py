import math
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


def _draw_speedometer(
    screen,
    rect,
    speed_kmh,
    max_kmh=140.0,
    start_angle_deg=225.0,
    sweep_deg=270.0,
):
    center = (rect.x + rect.width // 2, rect.y + rect.height // 2 + 10)
    radius = min(rect.width, rect.height) // 2 - 12
    pygame.draw.circle(screen, (25, 25, 28), center, radius)
    pygame.draw.circle(screen, PANEL_BORDER, center, radius, 2)

    ticks = [0, 20, 40, 60, 80, 100, 120, 140]
    font_tick = pygame.font.SysFont(None, 20)
    for value in ticks:
        t = value / max_kmh
        angle = math.radians(start_angle_deg - (t * sweep_deg))
        inner = (
            center[0] + int((radius - 12) * math.cos(angle)),
            center[1] - int((radius - 12) * math.sin(angle)),
        )
        outer = (
            center[0] + int(radius * math.cos(angle)),
            center[1] - int(radius * math.sin(angle)),
        )
        pygame.draw.line(screen, MUTED_TEXT, inner, outer, 2)
        label_pos = (
            center[0] + int((radius - 28) * math.cos(angle)),
            center[1] - int((radius - 28) * math.sin(angle)),
        )
        label = font_tick.render(str(value), True, MUTED_TEXT)
        label_rect = label.get_rect(center=label_pos)
        screen.blit(label, label_rect)

    speed = max(0.0, min(speed_kmh, max_kmh))
    needle_t = speed / max_kmh
    needle_angle = math.radians(start_angle_deg - (needle_t * sweep_deg))
    needle_end = (
        center[0] + int((radius - 18) * math.cos(needle_angle)),
        center[1] - int((radius - 18) * math.sin(needle_angle)),
    )
    pygame.draw.line(screen, SPEED_COLOR, center, needle_end, 4)
    pygame.draw.circle(screen, SPEED_COLOR, center, 5)

    font_speed = pygame.font.SysFont(None, 48)
    font_unit = pygame.font.SysFont(None, 20)
    speed_text = font_speed.render(f"{speed_kmh:.0f}", True, TEXT_COLOR)
    speed_rect = speed_text.get_rect(center=(center[0], rect.y + rect.height - 40))
    screen.blit(speed_text, speed_rect)
    unit_text = font_unit.render("KM/H", True, MUTED_TEXT)
    unit_rect = unit_text.get_rect(center=(center[0], rect.y + rect.height - 18))
    screen.blit(unit_text, unit_rect)


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
    x = 20
    y = 20
    line_gap = 22

    extra_lines = 2 if telemetry.selected_mode == "takeover" else 0
    panel_height = 260 + (extra_lines * line_gap)
    panel_rect = pygame.Rect(x, y, 360, panel_height)
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

    speed_rect = pygame.Rect(x, panel_rect.bottom + 10, 220, 160)
    _draw_speedometer(screen, speed_rect, telemetry.current_speed_kmh)
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
