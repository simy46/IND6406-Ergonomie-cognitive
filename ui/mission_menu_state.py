import pygame

from core.constants import (
    MODE_MANUAL,
    MODE_AUTOMATIC,
    MODE_TAKEOVER,
    NBACK_LEVEL,
    NBACK_INTERVAL_SECONDS,
)


def init_state():
    return {
        "name": "",
        "selected_mode": None,
        "traffic_enabled": True,
        "nback_enabled": True,
        "screen_step": 1,
        "selected_config": 0,
        "nback_level": int(NBACK_LEVEL),
        "nback_interval": float(NBACK_INTERVAL_SECONDS),
        "nback_rounds": None,
    }


def build_modes():
    return [
        (MODE_MANUAL, "Conduite manuelle"),
        (MODE_AUTOMATIC, "Conduite automatique"),
        (MODE_TAKEOVER, "Auto + reprise humaine"),
    ]


def build_popup_rect(width, height):
    return pygame.Rect(
        (width - 620) // 2,
        (height - 500) // 2,
        620,
        500,
    )
