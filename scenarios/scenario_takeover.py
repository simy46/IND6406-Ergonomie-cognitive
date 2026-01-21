import time
import pygame

from scenarios.takeover_audio import init_mixer, load_sound, play_sound
from scenarios.takeover_logic import (
    update_auto_only,
    detect_human_input,
    mark_manual_override,
)


class TakeoverController:
    def __init__(
        self,
        vehicle,
        autonomous_driver,
        wheel,
        min_delay=15.0,
        extra_random=15.0,
        sound_enabled="assets/noa_enabled.mp3",
        sound_disabled="assets/noa_disabled.mp3",
    ):
        self.vehicle = vehicle
        self.auto = autonomous_driver
        self.wheel = wheel

        self.start_time = time.time()
        self.takeover_delay = float(min_delay) + (time.time() % float(extra_random))

        self.takeover_requested = False
        self.takeover_done = False
        self.manual_override = False

        self.request_time = None
        self.reaction_time = None

        init_mixer()
        self.sound_enabled = load_sound(sound_enabled)
        self.sound_disabled = load_sound(sound_disabled)

        self.play_noa_enabled()
        print(f"[TAKEOVER] Autonomous ENABLED (delay={self.takeover_delay:.1f}s)")

    # -------------------------
    # sounds
    # -------------------------
    def play_noa_enabled(self):
        play_sound(self.sound_enabled)

    def play_noa_disabled(self):
        play_sound(self.sound_disabled)

    # -------------------------
    # logic
    # -------------------------
    def update_auto_only(self):
        update_auto_only(self)

    def should_request_manual(self) -> bool:
        """Le main peut utiliser ça pour forcer active_drive_mode='manual'."""
        return self.takeover_requested and not (self.takeover_done or self.manual_override)

    def detect_human_input(self, steer_eps=0.05, pedal_eps=0.05) -> bool:
        """Détecte une action humaine sur volant/pédales."""
        return detect_human_input(self, steer_eps, pedal_eps)

    def mark_manual_override(self, reason="human"):
        """
        Appelé quand :
        - ESC est pressé
        - OU humain commence à conduire
        """
        mark_manual_override(self, reason)

    def is_manual(self):
        return self.takeover_done or self.manual_override

    def get_reaction_time(self):
        return self.reaction_time
