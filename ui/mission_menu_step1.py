import pygame


def draw_step_name_mode(
    screen,
    popup_rect,
    fonts,
    name,
    modes,
    selected_mode,
    traffic_enabled,
):
    pop_x, pop_y = popup_rect.x, popup_rect.y
    screen.blit(
        fonts["main"].render("Nom :", True, (220, 220, 220)),
        (pop_x + 80, pop_y + 110),
    )
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        (pop_x + 80, pop_y + 145, 460, 40),
        2,
        border_radius=6,
    )
    screen.blit(
        fonts["main"].render(name, True, (255, 255, 255)),
        (pop_x + 90, pop_y + 152),
    )
    for i, (mode_key, label) in enumerate(modes):
        y = pop_y + 235 + i * 55
        is_selected = (selected_mode == mode_key)
        pygame.draw.rect(
            screen,
            (0, 160, 200) if is_selected else (50, 50, 50),
            (pop_x + 80, y, 460, 45),
            border_radius=8,
        )
        screen.blit(
            fonts["main"].render(label, True, (255, 255, 255)),
            (pop_x + 100, y + 10),
        )
    checkbox_x = pop_x + 80
    checkbox_y = pop_y + 235 + len(modes) * 55 + 10
    checkbox_size = 24
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        (checkbox_x, checkbox_y, checkbox_size, checkbox_size),
        2,
        border_radius=4,
    )
    if traffic_enabled:
        pygame.draw.rect(
            screen,
            (0, 180, 220),
            (checkbox_x + 4, checkbox_y + 4, checkbox_size - 8, checkbox_size - 8),
            border_radius=3,
        )
    traffic_label = "Activer trafic léger [F1]"
    screen.blit(
        fonts["main"].render(traffic_label, True, (220, 220, 220)),
        (checkbox_x + 36, checkbox_y - 2),
    )
    hint_surface = fonts["small"].render("ENTRÉE pour continuer", True, (180, 180, 180))
    hint_rect = hint_surface.get_rect(
        bottomright=(screen.get_width() - 24, screen.get_height() - 20)
    )
    screen.blit(hint_surface, hint_rect)
