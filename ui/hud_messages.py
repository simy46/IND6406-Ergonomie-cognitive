import pygame


def draw_hud_message(
    screen,
    text,
    position=(200, 30),
    color=(0, 220, 255),
    font_size=36,
):
    font = pygame.font.SysFont(None, font_size)
    msg = font.render(text, True, color)
    screen.blit(msg, position)


def draw_center_message(screen, text, color=(0, 220, 255), font_size=40):
    font = pygame.font.SysFont(None, font_size)
    msg = font.render(text, True, color)
    rect = msg.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(msg, rect)
