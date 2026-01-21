import pygame


def handle_step1_event(
    event,
    popup_rect,
    modes,
    name,
    selected_mode,
    traffic_enabled,
    nback_enabled,
):
    go_next = False
    exit_app = False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            exit_app = True
        elif event.key == pygame.K_BACKSPACE:
            name = name[:-1]
        elif event.key == pygame.K_RETURN:
            if name.strip():
                go_next = True
        elif event.unicode.isprintable() and len(name) < 20:
            name += event.unicode
    if event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = event.pos
        for i, (mode_key, _) in enumerate(modes):
            bx = popup_rect.x + 80
            by = popup_rect.y + 220 + i * 55
            bw, bh = 440, 45
            if bx <= mx <= bx + bw and by <= my <= by + bh:
                selected_mode = mode_key
        checkbox_x = popup_rect.x + 80
        checkbox_y = popup_rect.y + 220 + len(modes) * 55 + 10
        checkbox_size = 24
        if (
            checkbox_x <= mx <= checkbox_x + checkbox_size
            and checkbox_y <= my <= checkbox_y + checkbox_size
        ):
            traffic_enabled = not traffic_enabled
        nback_box_x = popup_rect.x + 80
        nback_box_y = checkbox_y + 40
        if (
            nback_box_x <= mx <= nback_box_x + checkbox_size
            and nback_box_y <= my <= nback_box_y + checkbox_size
        ):
            nback_enabled = not nback_enabled
    return name, selected_mode, traffic_enabled, nback_enabled, go_next, exit_app


def handle_step2_event(event, selected_config, nback_level, nback_interval, nback_rounds):
    go_back = False
    start_mission = False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            go_back = True
        elif event.key == pygame.K_RETURN:
            start_mission = True
        elif event.key == pygame.K_UP:
            selected_config = (selected_config - 1) % 3
        elif event.key == pygame.K_DOWN:
            selected_config = (selected_config + 1) % 3
        elif event.key in (pygame.K_RIGHT, pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
            if selected_config == 0:
                nback_level += 1
            elif selected_config == 1:
                nback_interval = max(0.5, nback_interval + 0.5)
            else:
                if nback_rounds is None:
                    nback_rounds = 1
                else:
                    nback_rounds += 1
        elif event.key in (pygame.K_LEFT, pygame.K_MINUS, pygame.K_KP_MINUS):
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
    return selected_config, nback_level, nback_interval, nback_rounds, go_back, start_mission
