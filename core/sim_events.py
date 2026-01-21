import pygame


def process_events(events, mission_manager, pause_controller, camera, hud_visible):
    running = True
    pause_clicks = []
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if mission_manager.mission_active:
                    pause_controller.toggle()
                continue
            if event.key == pygame.K_p:
                if mission_manager.mission_active and not pause_controller.paused:
                    mission_manager.handle_escape()
                continue
            if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                hud_visible = not hud_visible
                continue
            if pause_controller.paused:
                continue
            if event.key == pygame.K_TAB:
                camera.toggle()
            elif mission_manager.show_restart_prompt and event.key == pygame.K_SPACE:
                mission_manager.reset_state_to_menu()
        elif pause_controller.paused and event.type == pygame.MOUSEBUTTONDOWN:
            pause_clicks.append(event.pos)
    return running, hud_visible, pause_clicks
