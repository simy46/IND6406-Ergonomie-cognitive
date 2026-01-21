import pygame

from ui.mission_menu_events import handle_step1_event, handle_step2_event
from ui.mission_menu_render import draw_overlay, draw_popup_frame, build_fonts
from ui.mission_menu_state import init_state, build_modes, build_popup_rect
from ui.mission_menu_step1 import draw_step_name_mode
from ui.mission_menu_step2 import draw_step_nback_config


def mission_popup(screen, clock):
    fonts = build_fonts()
    state = init_state()
    modes = build_modes()

    while True:
        clock.tick(60)
        width, height = screen.get_size()
        popup_rect = build_popup_rect(width, height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None, None, None, None
            if state["screen_step"] == 1:
                (
                    state["name"],
                    state["selected_mode"],
                    state["traffic_enabled"],
                    state["nback_enabled"],
                    go_next,
                    exit_app,
                ) = handle_step1_event(
                    event,
                    popup_rect,
                    modes,
                    state["name"],
                    state["selected_mode"],
                    state["traffic_enabled"],
                    state["nback_enabled"],
                )
                if exit_app:
                    return None, None, None, None, None
                if go_next and state["name"].strip() and state["selected_mode"]:
                    if state["nback_enabled"]:
                        state["screen_step"] = 2
                    else:
                        return (
                            state["name"].strip(),
                            state["selected_mode"],
                            state["traffic_enabled"],
                            None,
                            False,
                        )
            else:
                (
                    state["selected_config"],
                    state["nback_level"],
                    state["nback_interval"],
                    state["nback_rounds"],
                    go_back,
                    start_mission,
                ) = handle_step2_event(
                    event,
                    state["selected_config"],
                    state["nback_level"],
                    state["nback_interval"],
                    state["nback_rounds"],
                )
                if go_back:
                    state["screen_step"] = 1
                if start_mission and state["name"].strip() and state["selected_mode"]:
                    rounds_value = (
                        state["nback_rounds"] if state["nback_rounds"] is not None else None
                    )
                    return (
                        state["name"].strip(),
                        state["selected_mode"],
                        state["traffic_enabled"],
                        {
                            "level": state["nback_level"],
                            "interval": state["nback_interval"],
                            "rounds": rounds_value,
                        },
                        True,
                    )

        draw_overlay(screen, width, height)
        popup_rect = draw_popup_frame(screen, width, height, fonts)

        if state["screen_step"] == 1:
            draw_step_name_mode(
                screen,
                popup_rect,
                fonts,
                state["name"],
                modes,
                state["selected_mode"],
                state["traffic_enabled"],
                state["nback_enabled"],
            )
        else:
            draw_step_nback_config(
                screen,
                popup_rect,
                fonts,
                state["nback_level"],
                state["nback_interval"],
                state["nback_rounds"],
                state["selected_config"],
                width,
                height,
            )

        pygame.display.flip()
