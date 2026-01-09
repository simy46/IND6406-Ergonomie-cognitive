import pygame
from core.constants import MODE_MANUAL, MODE_AUTOMATIC, MODE_TAKEOVER


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
                return None, None, None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_RETURN:
                    if name.strip() and selected_mode:
                        return name.strip(), selected_mode, traffic_enabled
                elif event.unicode.isprintable() and len(name) < 20:
                    name += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
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
        screen.blit(
            font_subtitle.render("Nouvelle mission", True, (200, 200, 200)),
            (POP_X + 210, POP_Y + 60)
        )

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
        screen.blit(
            font.render("Activer trafic léger", True, (220, 220, 220)),
            (checkbox_x + 36, checkbox_y - 2)
        )

        # =========================
        # FOOTER
        # =========================
        hint = "Cliquez sur [ENTRÉE] pour démarrer la mission"
        if not (name.strip() and selected_mode):
            hint = "Entrez un nom et choisissez un mode"

        screen.blit(
            font_small.render(hint, True, (180, 180, 180)),
            (POP_X + 150, POP_Y + POP_H - 35)
        )

        pygame.display.flip()
