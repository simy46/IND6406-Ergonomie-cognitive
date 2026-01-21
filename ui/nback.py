import pygame

from core.constants import NBACK_STIMULUS_OFF_GAP_SECONDS


def render_nback(screen, task, elapsed_seconds=None):
    if task is None or task.completed or task.current_position is None:
        return

    width, height = screen.get_size()
    padding = max(16, int(min(width, height) * 0.03))
    box_size = int(min(width, height) * 0.117)
    box_size = max(28, min(box_size, 64))
    gap = max(10, int(box_size * 0.35))

    total_width = (box_size * task.positions) + (gap * (task.positions - 1))
    x_start = width - padding - total_width
    y_start = padding

    panel_w = total_width + 16
    panel_h = box_size + 18
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 0))
    pygame.draw.rect(panel, (0, 0, 0, 140), panel.get_rect(), border_radius=8)
    screen.blit(panel, (x_start - 8, y_start - 8))

    base_color = (30, 30, 32)
    outline = (200, 200, 200)
    active_fill = (0, 220, 255)
    active_outline = (255, 255, 255)

    flash_color = None
    if elapsed_seconds is not None and task.last_response_time is not None:
        if (elapsed_seconds - task.last_response_time) <= 0.25:
            if task.last_response_kind == "hit":
                flash_color = (0, 200, 120)
            elif task.last_response_kind == "false_alarm":
                flash_color = (220, 80, 80)
            else:
                flash_color = (170, 170, 170)

    show_active = True
    if elapsed_seconds is not None and task.current_start_time is not None:
        on_duration = max(0.0, task.interval_seconds - NBACK_STIMULUS_OFF_GAP_SECONDS)
        if (elapsed_seconds - task.current_start_time) >= on_duration:
            show_active = False

    pulse_alpha = 0
    if elapsed_seconds is not None and task.current_start_time is not None:
        elapsed_since_start = elapsed_seconds - task.current_start_time
        if elapsed_since_start < 0.35:
            pulse_alpha = int(90 * (1.0 - (elapsed_since_start / 0.35)))

    for index in range(task.positions):
        x = x_start + index * (box_size + gap)
        rect = pygame.Rect(x, y_start, box_size, box_size)
        if show_active and index == task.current_position:
            pygame.draw.rect(screen, active_fill, rect, border_radius=6)
            pygame.draw.rect(screen, active_outline, rect, 2, border_radius=6)
            if pulse_alpha > 0:
                pulse_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
                pulse_surface.fill((255, 255, 255, pulse_alpha))
                screen.blit(pulse_surface, rect.topleft)
        else:
            pygame.draw.rect(screen, base_color, rect, border_radius=6)
            pygame.draw.rect(screen, outline, rect, 2, border_radius=6)

    if flash_color is not None:
        flash_rect = pygame.Rect(x_start - 10, y_start - 10, total_width + 20, box_size + 20)
        pygame.draw.rect(screen, flash_color, flash_rect, 2, border_radius=8)
