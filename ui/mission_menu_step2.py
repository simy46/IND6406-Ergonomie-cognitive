import pygame


def draw_step_nback_config(
    screen,
    popup_rect,
    fonts,
    nback_level,
    nback_interval,
    nback_rounds,
    selected_config,
    width,
    height,
):
    pop_x, pop_y = popup_rect.x, popup_rect.y
    screen.blit(
        fonts["main"].render("Configuration N-Back", True, (220, 220, 220)),
        (pop_x + 80, pop_y + 120),
    )
    pygame.draw.rect(
        screen,
        (40, 40, 40),
        (pop_x + 60, pop_y + 165, 500, 180),
        border_radius=10,
    )
    label_color = (0, 220, 255)
    value_color = (255, 255, 255)
    inactive_color = (180, 180, 180)

    def draw_config_line(label, value, y_pos, selected):
        color = label_color if selected else inactive_color
        screen.blit(fonts["main"].render(label, True, color), (pop_x + 80, y_pos))
        screen.blit(fonts["main"].render(value, True, value_color), (pop_x + 360, y_pos))

    rounds_text = "Fin mission" if nback_rounds is None else str(nback_rounds)
    draw_config_line("N-Back niveau", f"{nback_level}", pop_y + 185, selected_config == 0)
    draw_config_line("Intervalle (s)", f"{nback_interval:.1f}", pop_y + 235, selected_config == 1)
    draw_config_line("Nombre de tours", rounds_text, pop_y + 285, selected_config == 2)

    nav_hint = "UP/DOWN: selection | LEFT/RIGHT: ajuster"
    nav_surface = fonts["small"].render(nav_hint, True, (160, 160, 160))
    nav_rect = nav_surface.get_rect(bottomleft=(24, height - 44))
    screen.blit(nav_surface, nav_rect)

    back_surface = fonts["small"].render("ESC pour revenir", True, (180, 180, 180))
    back_rect = back_surface.get_rect(bottomleft=(24, height - 20))
    screen.blit(back_surface, back_rect)
    start_surface = fonts["small"].render(
        "ENTRÉE pour démarrer la mission",
        True,
        (180, 180, 180),
    )
    start_rect = start_surface.get_rect(bottomright=(width - 24, height - 20))
    screen.blit(start_surface, start_rect)
