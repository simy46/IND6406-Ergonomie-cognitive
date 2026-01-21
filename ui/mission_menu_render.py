import pygame


def build_fonts():
    return {
        "title": pygame.font.SysFont(None, 44),
        "subtitle": pygame.font.SysFont(None, 28),
        "main": pygame.font.SysFont(None, 32),
        "small": pygame.font.SysFont(None, 22),
    }


def draw_overlay(screen, width, height):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))


def draw_popup_frame(screen, width, height, fonts):
    pop_w, pop_h = 620, 500
    pop_x = (width - pop_w) // 2
    pop_y = (height - pop_h) // 2
    rect = pygame.Rect(pop_x, pop_y, pop_w, pop_h)
    pygame.draw.rect(screen, (25, 25, 25), rect, border_radius=12)
    pygame.draw.rect(screen, (0, 180, 220), rect, 2, border_radius=12)
    screen.blit(
        fonts["title"].render("IND6406 - Ergonomie cognitive", True, (0, 220, 255)),
        (pop_x + 70, pop_y + 20),
    )
    return rect
