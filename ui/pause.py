import pygame


def render_pause_screen(screen, message="PAUSE: Clique sur [P] pour continuer"):
    width, height = screen.get_size()
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 44)
    text = font.render(message, True, (220, 220, 220))
    rect = text.get_rect(center=(width // 2, height // 2))
    screen.blit(text, rect)
