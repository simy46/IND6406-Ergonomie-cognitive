import math
import pygame

from ui.hud_style import PANEL_BG, PANEL_BORDER, TEXT_COLOR, MUTED_TEXT, SPEED_COLOR


def draw_panel(screen, rect, border_color=PANEL_BORDER, fill_color=PANEL_BG, radius=10):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    panel.fill((0, 0, 0, 0))
    pygame.draw.rect(panel, fill_color, panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, border_color, panel.get_rect(), 2, border_radius=radius)
    screen.blit(panel, rect.topleft)


def draw_speedometer(
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
