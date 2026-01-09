import math
import pygame


PANEL_BG = (15, 15, 18, 215)
PANEL_BORDER = (0, 180, 220)
TEXT_COLOR = (235, 235, 235)
MUTED_TEXT = (120, 200, 215)
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


def draw_center_message(screen, text, color=(0, 220, 255), font_size=40):
    font = pygame.font.SysFont(None, font_size)
    msg = font.render(text, True, color)
    rect = msg.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(msg, rect)


def render_hud(screen, telemetry, active_drive_mode):
    if telemetry is None:
        return
    font = pygame.font.SysFont(None, 24)
    font_small = pygame.font.SysFont(None, 20)
    font_name = pygame.font.SysFont(None, 30)
    x = 20
    y = 20
    line_gap = 22

    panel_height = 230
    panel_rect = pygame.Rect(x, y, 380, panel_height)
    _draw_panel(screen, panel_rect)
    content_x = panel_rect.x + 16
    content_y = panel_rect.y + 14

    elapsed = telemetry.get_mission_elapsed_seconds()
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    timer_text = f"{minutes:02d}:{seconds:02d}"
    name_text = font_name.render(telemetry.student_name, True, TEXT_COLOR)
    screen.blit(name_text, (content_x, content_y))
    content_y += line_gap + 6

    scenario_key = font_small.render("Scenario", True, MUTED_TEXT)
    drive_key = font_small.render("Drive mode", True, MUTED_TEXT)
    screen.blit(scenario_key, (content_x, content_y))
    screen.blit(drive_key, (content_x + 180, content_y))
    content_y += line_gap - 6
    scenario_text = font.render(telemetry.selected_mode, True, TEXT_COLOR)
    drive_text = font.render(active_drive_mode, True, TEXT_COLOR)
    screen.blit(scenario_text, (content_x, content_y))
    screen.blit(drive_text, (content_x + 180, content_y))
    content_y += line_gap + 8

    grid_x1 = content_x
    grid_x2 = content_x + 190
    row1_y = content_y
    row2_y = content_y + line_gap
    row3_y = content_y + (line_gap * 2)

    on_route_text = font.render(
        f"On route {telemetry.get_percent_in_lane():.1f}%",
        True,
        TEXT_COLOR,
    )
    screen.blit(on_route_text, (grid_x1, row1_y))
    offset_text = font.render(
        f"Avg offset {telemetry.get_lane_offset_mean():.2f} m",
        True,
        TEXT_COLOR,
    )
    screen.blit(offset_text, (grid_x1, row2_y))
    time_split_text = font.render(
        f"Manual {telemetry.manual_time_seconds:.1f}s  Auto {telemetry.auto_time_seconds:.1f}s",
        True,
        TEXT_COLOR,
    )
    screen.blit(time_split_text, (grid_x1, row3_y))

    invasions_text = font.render(
        f"Lane inv. {telemetry.lane_invasion_count}",
        True,
        TEXT_COLOR,
    )
    screen.blit(invasions_text, (grid_x2, row1_y))
    collisions_text = font.render(
        f"Collisions {telemetry.collision_count}",
        True,
        TEXT_COLOR,
    )
    screen.blit(collisions_text, (grid_x2, row2_y))
    if telemetry.selected_mode == "takeover":
        requested = "YES" if telemetry.takeover_requested else "NO"
        reaction = telemetry.get_takeover_reaction_time()
        reaction_text = "N/A" if reaction is None else f"{reaction:.2f}s"
        takeover_text = font.render(
            f"Takeover {requested} {reaction_text}",
            True,
            TEXT_COLOR,
        )
        screen.blit(takeover_text, (grid_x2, row3_y))

    timer_big = pygame.font.SysFont(None, 48).render(timer_text, True, SPEED_COLOR)
    time_rect = timer_big.get_rect(bottomright=(screen.get_width() - 20, screen.get_height() - 20))
    screen.blit(timer_big, time_rect)
    distance_big = pygame.font.SysFont(None, 48).render(
        f"{telemetry.distance_traveled_meters:.1f} m",
        True,
        TEXT_COLOR,
    )
    distance_rect = distance_big.get_rect(bottomright=(screen.get_width() - 20, time_rect.top - 10))
    screen.blit(distance_big, distance_rect)

    speed_rect = pygame.Rect(16, screen.get_height() - 200, 260, 190)
    _draw_speedometer(screen, speed_rect, telemetry.current_speed_kmh)
