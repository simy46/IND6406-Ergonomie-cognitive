import time
import pygame

from scenarios.takeover_audio import init_mixer, load_sound, play_sound
from scenarios.takeover_logic import (
    update_auto_only,
    detect_human_input,
    mark_manual_override,
    toggle_mode,
)


class TakeoverController:
    def __init__(
        self,
        vehicle,
        autonomous_driver,
        wheel,
        sound_enabled="assets/noa_enabled.mp3",
        sound_disabled="assets/noa_disabled.mp3",
    ):
        self.vehicle = vehicle
        self.auto = autonomous_driver
        self.wheel = wheel

        self.takeover_requested = False
        self.takeover_done = False
        self.manual_override = False

        self.request_time = None
        self.reaction_time = None

        init_mixer()
        self.sound_enabled = load_sound(sound_enabled)
        self.sound_disabled = load_sound(sound_disabled)

        self.play_noa_enabled()
        print("[TAKEOVER] Autonomous ENABLED")

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

    def toggle_mode(self, active_drive_mode):
        return toggle_mode(self, active_drive_mode)

    def should_request_manual(self) -> bool:
        """Le main peut utiliser ça pour forcer active_drive_mode='manual'."""
        return False

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
