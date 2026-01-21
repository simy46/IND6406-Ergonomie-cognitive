import pygame

from core.constants import MODE_TAKEOVER
from ui.hud_style import TEXT_COLOR, MUTED_TEXT, SPEED_COLOR


def draw_header(screen, telemetry, active_drive_mode, font, font_small, font_name, x, y, line_gap):
    name_text = font_name.render(telemetry.student_name, True, TEXT_COLOR)
    screen.blit(name_text, (x, y))
    y += line_gap + 6

    scenario_key = font_small.render("Scenario", True, MUTED_TEXT)
    drive_key = font_small.render("Drive mode", True, MUTED_TEXT)
    screen.blit(scenario_key, (x, y))
    screen.blit(drive_key, (x + 180, y))
    y += line_gap - 6
    scenario_text = font.render(telemetry.selected_mode, True, TEXT_COLOR)
    drive_text = font.render(active_drive_mode, True, TEXT_COLOR)
    screen.blit(scenario_text, (x, y))
    screen.blit(drive_text, (x + 180, y))
    y += line_gap + 8
    return y


def draw_stats_blocks(screen, telemetry, font, font_small, content_x, content_y, line_gap):
    block_gap = 28
    col_gap = block_gap
    col_width = 160
    col1_x = content_x
    col2_x = content_x + col_width + col_gap
    block_height = (line_gap * 2) + 6
    row_gap = block_height + block_gap
    row1_y = content_y
    row2_y = content_y + row_gap

    def draw_block(label, lines, x_pos, y_pos):
        key = font_small.render(label, True, MUTED_TEXT)
        screen.blit(key, (x_pos, y_pos))
        line_y = y_pos + line_gap - 6
        for line in lines:
            val = font.render(line, True, TEXT_COLOR)
            screen.blit(val, (x_pos, line_y))
            line_y += line_gap

    draw_block(
        "Route tracking",
        [
            f"On route {telemetry.get_percent_in_lane():.1f}%",
            f"Avg offset {telemetry.get_lane_offset_mean():.2f} m",
        ],
        col1_x,
        row1_y,
    )
    draw_block(
        "Incidents",
        [
            f"Lane invasions {telemetry.lane_invasion_count}",
            f"Collisions {telemetry.collision_count}",
        ],
        col2_x,
        row1_y,
    )
    draw_block(
        "Time split",
        [
            f"Manual {telemetry.manual_time_seconds:.1f}s",
            f"Auto {telemetry.auto_time_seconds:.1f}s",
        ],
        col1_x,
        row2_y,
    )
    if telemetry.selected_mode == MODE_TAKEOVER:
        requested = "YES" if telemetry.takeover_requested else "NO"
        reaction = telemetry.get_takeover_reaction_time()
        reaction_text = "N/A" if reaction is None else f"{reaction:.2f}s"
        draw_block(
            "Takeover",
            [f"Requested {requested}", f"Reaction {reaction_text}"],
            col2_x,
            row2_y,
        )


def draw_timer_distance(screen, telemetry, timer_text):
    timer_big = pygame.font.SysFont(None, 48).render(timer_text, True, SPEED_COLOR)
    time_rect = timer_big.get_rect(bottomright=(screen.get_width() - 20, screen.get_height() - 20))
    screen.blit(timer_big, time_rect)
    distance_big = pygame.font.SysFont(None, 38).render(
        f"{telemetry.distance_traveled_meters:.1f} m",
        True,
        TEXT_COLOR,
    )
    distance_rect = distance_big.get_rect(bottomright=(screen.get_width() - 20, time_rect.top - 10))
    screen.blit(distance_big, distance_rect)
