import pygame


def render_pause_screen(screen, message="PAUSE: Clique sur [ESC] pour continuer"):
    width, height = screen.get_size()
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 44)
    button_font = pygame.font.SysFont(None, 32)

    text = font.render(message, True, (220, 220, 220))
    rect = text.get_rect(center=(width // 2, height // 2 - 40))
    screen.blit(text, rect)

    btn_w, btn_h = 260, 44
    btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
    btn_rect.center = (width // 2, height // 2 + 30)
    pygame.draw.rect(screen, (0, 160, 200), btn_rect, border_radius=8)
    label = button_font.render("Retour au menu", True, (255, 255, 255))
    label_rect = label.get_rect(center=btn_rect.center)
    screen.blit(label, label_rect)

    return btn_rect
