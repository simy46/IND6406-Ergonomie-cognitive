import pygame


def init_mixer():
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except Exception as e:
        print(f"[TAKEOVER][WARN] pygame.mixer.init failed: {e}")


def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"[TAKEOVER][WARN] Loading sounds failed: {e}")
        return None


def play_sound(sound):
    if sound:
        try:
            sound.play()
        except Exception:
            pass
