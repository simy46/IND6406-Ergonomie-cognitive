import pygame

from ui.hud_blocks import draw_header, draw_stats_blocks, draw_timer_distance
from ui.hud_draw import draw_panel, draw_speedometer
from ui.hud_style import TEXT_COLOR


def render_hud(screen, telemetry, active_drive_mode, hud_visible=True):
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
    if hud_visible:
        draw_panel(screen, panel_rect)
    content_x = panel_rect.x + 16
    content_y = panel_rect.y + 14

    elapsed = telemetry.get_mission_elapsed_seconds()
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    timer_text = f"{minutes:02d}:{seconds:02d}"
    if hud_visible:
        content_y = draw_header(
            screen,
            telemetry,
            active_drive_mode,
            font,
            font_small,
            font_name,
            content_x,
            content_y,
            line_gap,
        )
        draw_stats_blocks(screen, telemetry, font, font_small, content_x, content_y, line_gap)

    draw_timer_distance(screen, telemetry, timer_text)

    speed_rect = pygame.Rect(16, screen.get_height() - 200, 260, 190)
    draw_speedometer(screen, speed_rect, telemetry.current_speed_kmh)
