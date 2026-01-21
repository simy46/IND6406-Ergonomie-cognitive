import pygame


_INIT_DONE = False
_SOUND_ENABLED = None
_SOUND_DISABLED = None


def _init():
    global _INIT_DONE, _SOUND_ENABLED, _SOUND_DISABLED
    if _INIT_DONE:
        return
    _INIT_DONE = True
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        _SOUND_ENABLED = pygame.mixer.Sound("assets/noa_enabled.mp3")
        _SOUND_DISABLED = pygame.mixer.Sound("assets/noa_disabled.mp3")
    except Exception as e:
        print(f"[MODE][WARN] Sound init failed: {e}")
        _SOUND_ENABLED = None
        _SOUND_DISABLED = None


def play_enabled():
    _init()
    if _SOUND_ENABLED:
        try:
            _SOUND_ENABLED.play()
        except Exception:
            pass


def play_disabled():
    _init()
    if _SOUND_DISABLED:
        try:
            _SOUND_DISABLED.play()
        except Exception:
            pass
