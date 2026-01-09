import time
import pygame


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

        # mixer safe init
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"[TAKEOVER][WARN] pygame.mixer.init failed: {e}")

        self.sound_enabled = None
        self.sound_disabled = None
        try:
            self.sound_enabled = pygame.mixer.Sound(sound_enabled)
            self.sound_disabled = pygame.mixer.Sound(sound_disabled)
        except Exception as e:
            print(f"[TAKEOVER][WARN] Loading sounds failed: {e}")

        self.play_noa_enabled()
        print(f"[TAKEOVER] Autonomous ENABLED (delay={self.takeover_delay:.1f}s)")

    # -------------------------
    # sounds
    # -------------------------
    def play_noa_enabled(self):
        if self.sound_enabled:
            try:
                self.sound_enabled.play()
            except Exception:
                pass

    def play_noa_disabled(self):
        if self.sound_disabled:
            try:
                self.sound_disabled.play()
            except Exception:
                pass

    # -------------------------
    # logic
    # -------------------------
    def update_auto_only(self):
        now = time.time()

        if self.takeover_done or self.manual_override:
            return

        self.auto.run_step()

        if (not self.takeover_requested) and ((now - self.start_time) >= self.takeover_delay):
            self.takeover_requested = True
            self.request_time = now
            self.play_noa_disabled()
            print("[TAKEOVER] Reprise demandée (NOA disabled)")

    def should_request_manual(self) -> bool:
        """Le main peut utiliser ça pour forcer active_drive_mode='manual'."""
        return self.takeover_requested and not (self.takeover_done or self.manual_override)

    def detect_human_input(self, steer_eps=0.05, pedal_eps=0.05) -> bool:
        """Détecte une action humaine sur volant/pédales."""
        if not self.wheel:
            return False

        control = self.wheel.get_control()
        return (
            abs(control.steer) > steer_eps
            or control.throttle > pedal_eps
            or control.brake > pedal_eps
        )

    def mark_manual_override(self, reason="human"):
        """
        Appelé quand :
        - ESC est pressé
        - OU humain commence à conduire
        """
        if self.takeover_done:
            return

        now = time.time()

        # takeover demandé -> calcul reaction time
        if self.takeover_requested and self.request_time is not None:
            if self.reaction_time is None:
                self.reaction_time = now - self.request_time
            self.takeover_done = True
            print(f"[TAKEOVER] Repris en {self.reaction_time:.2f}s ({reason})")
        else:
            # override manuel avant la demande
            self.manual_override = True
            print(f"[TAKEOVER] Manual override ({reason})")

        # si on passe en manuel, NOA est off
        self.play_noa_disabled()

    def is_manual(self):
        return self.takeover_done or self.manual_override

    def get_reaction_time(self):
        return self.reaction_time
