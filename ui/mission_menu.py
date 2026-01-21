import pygame
from core.constants import (
    MODE_MANUAL,
    MODE_AUTOMATIC,
    MODE_TAKEOVER,
    NBACK_LEVEL,
    NBACK_INTERVAL_SECONDS,
    NBACK_TOTAL_TRIALS,
)


def mission_popup(screen, clock):
    WIDTH, HEIGHT = screen.get_size()
    POP_W, POP_H = 620, 500
    POP_X = (WIDTH - POP_W) // 2
    POP_Y = (HEIGHT - POP_H) // 2

    font_title = pygame.font.SysFont(None, 44)
    font_subtitle = pygame.font.SysFont(None, 28)
    font = pygame.font.SysFont(None, 32)
    font_small = pygame.font.SysFont(None, 22)

    name = ""
    selected_mode = None
    traffic_enabled = False
    screen_step = 1
    selected_config = 0
    nback_level = int(NBACK_LEVEL)
    nback_interval = float(NBACK_INTERVAL_SECONDS)
    nback_rounds = int(NBACK_TOTAL_TRIALS)

    modes = [
        (MODE_MANUAL, "Conduite manuelle"),
        (MODE_AUTOMATIC, "Conduite automatique"),
        (MODE_TAKEOVER, "Auto + reprise humaine"),
    ]

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None, None, None

            if event.type == pygame.KEYDOWN:
                if screen_step == 1:
                    if event.key == pygame.K_ESCAPE:
                        return None, None, None, None
                    if event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if name.strip():
                            screen_step = 2
                    elif event.unicode.isprintable() and len(name) < 20:
                        name += event.unicode
                else:
                    if event.key == pygame.K_ESCAPE:
                        screen_step = 1
                    elif event.key == pygame.K_RETURN:
                        if name.strip() and selected_mode:
                            rounds_value = nback_rounds if nback_rounds is not None else None
                            return (
                                name.strip(),
                                selected_mode,
                                traffic_enabled,
                                {
                                    "level": nback_level,
                                    "interval": nback_interval,
                                    "rounds": rounds_value,
                                },
                            )
                    elif event.key == pygame.K_LEFT:
                        selected_config = (selected_config - 1) % 3
                    elif event.key == pygame.K_RIGHT:
                        selected_config = (selected_config + 1) % 3
                    elif event.key in (pygame.K_UP, pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                        if selected_config == 0:
                            nback_level += 1
                        elif selected_config == 1:
                            nback_interval = max(0.5, nback_interval + 0.5)
                        else:
                            if nback_rounds is None:
                                nback_rounds = 1
                            else:
                                nback_rounds += 1
                    elif event.key in (pygame.K_DOWN, pygame.K_MINUS, pygame.K_KP_MINUS):
                        if selected_config == 0:
                            nback_level -= 1
                        elif selected_config == 1:
                            nback_interval = max(0.5, nback_interval - 0.5)
                        else:
                            if nback_rounds is None:
                                nback_rounds = 1
                            elif nback_rounds <= 1:
                                nback_rounds = None
                            else:
                                nback_rounds -= 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if screen_step == 1:
                    for i, (mode_key, _) in enumerate(modes):
                        bx = POP_X + 80
                        by = POP_Y + 220 + i * 55
                        bw, bh = 440, 45
                        if bx <= mx <= bx + bw and by <= my <= by + bh:
                            selected_mode = mode_key
                    checkbox_x = POP_X + 80
                    checkbox_y = POP_Y + 220 + len(modes) * 55 + 10
                    checkbox_size = 24
                    if (
                        checkbox_x <= mx <= checkbox_x + checkbox_size
                        and checkbox_y <= my <= checkbox_y + checkbox_size
                    ):
                        traffic_enabled = not traffic_enabled

        # =========================
        # DRAW OVERLAY
        # =========================
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        # =========================
        # POPUP BACKGROUND
        # =========================
        pygame.draw.rect(
            screen,
            (25, 25, 25),
            (POP_X, POP_Y, POP_W, POP_H),
            border_radius=12
        )
        pygame.draw.rect(
            screen,
            (0, 180, 220),
            (POP_X, POP_Y, POP_W, POP_H),
            2,
            border_radius=12
        )

        # =========================
        # TITLE
        # =========================
        screen.blit(
            font_title.render("IND6406 - Ergonomie cognitive", True, (0, 220, 255)),
            (POP_X + 70, POP_Y + 20)
        )

        if screen_step == 1:
            # =========================
            # NAME INPUT
            # =========================
            screen.blit(
                font.render("Nom :", True, (220, 220, 220)),
                (POP_X + 80, POP_Y + 110)
            )

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (POP_X + 80, POP_Y + 145, 460, 40),
                2,
                border_radius=6
            )

            screen.blit(
                font.render(name, True, (255, 255, 255)),
                (POP_X + 90, POP_Y + 152)
            )

            # =========================
            # MODE BUTTONS
            # =========================
            for i, (mode_key, label) in enumerate(modes):
                y = POP_Y + 235 + i * 55
                is_selected = (selected_mode == mode_key)

                pygame.draw.rect(
                    screen,
                    (0, 160, 200) if is_selected else (50, 50, 50),
                    (POP_X + 80, y, 460, 45),
                    border_radius=8
                )

                screen.blit(
                    font.render(label, True, (255, 255, 255)),
                    (POP_X + 100, y + 10)
                )

            checkbox_x = POP_X + 80
            checkbox_y = POP_Y + 235 + len(modes) * 55 + 10
            checkbox_size = 24
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (checkbox_x, checkbox_y, checkbox_size, checkbox_size),
                2,
                border_radius=4
            )
            if traffic_enabled:
                pygame.draw.rect(
                    screen,
                    (0, 180, 220),
                    (checkbox_x + 4, checkbox_y + 4, checkbox_size - 8, checkbox_size - 8),
                    border_radius=3
                )
            traffic_label = "Activer trafic léger [F1]"
            screen.blit(
                font.render(traffic_label, True, (220, 220, 220)),
                (checkbox_x + 36, checkbox_y - 2)
            )

            # =========================
            # FOOTER
            # =========================
            hint_surface = font_small.render("ENTRÉE pour continuer", True, (180, 180, 180))
            hint_rect = hint_surface.get_rect(
                bottomright=(WIDTH - 24, HEIGHT - 20)
            )
            screen.blit(hint_surface, hint_rect)
        else:
            # =========================
            # N-BACK CONFIG
            # =========================
            screen.blit(
                font.render("Configuration N-Back", True, (220, 220, 220)),
                (POP_X + 80, POP_Y + 120)
            )

            label_color = (0, 220, 255)
            value_color = (255, 255, 255)
            inactive_color = (180, 180, 180)

            def draw_config_line(label, value, y_pos, selected):
                color = label_color if selected else inactive_color
                screen.blit(font.render(label, True, color), (POP_X + 80, y_pos))
                screen.blit(font.render(value, True, value_color), (POP_X + 360, y_pos))

            rounds_text = "Jusqu'à la fin de mission" if nback_rounds is None else str(nback_rounds)
            draw_config_line("N-Back niveau", f"{nback_level}", POP_Y + 185, selected_config == 0)
            draw_config_line("Intervalle (s)", f"{nback_interval:.1f}", POP_Y + 235, selected_config == 1)
            draw_config_line("Nombre de tours", rounds_text, POP_Y + 285, selected_config == 2)

            nav_hint = "←/→ sélection | ↑/↓ ajuster"
            screen.blit(
                font_small.render(nav_hint, True, (160, 160, 160)),
                (POP_X + 80, POP_Y + 345)
            )

            back_surface = font_small.render("ESC pour revenir", True, (180, 180, 180))
            back_rect = back_surface.get_rect(
                bottomleft=(24, HEIGHT - 20)
            )
            screen.blit(back_surface, back_rect)
            start_surface = font_small.render("ENTRÉE pour démarrer la mission", True, (180, 180, 180))
            start_rect = start_surface.get_rect(
                bottomright=(WIDTH - 24, HEIGHT - 20)
            )
            screen.blit(start_surface, start_rect)

        pygame.display.flip()
