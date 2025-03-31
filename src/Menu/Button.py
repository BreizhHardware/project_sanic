from pygame.locals import *
import pygame


class Button:
    def __init__(self, text, x, y, width, height, action=None, locked=False):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action
        self.hover = False
        self.locked = locked
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, font):
        # Button colors
        if self.locked:
            bg_color = (100, 100, 100)
            text_color = (200, 200, 200)
        elif self.hover:
            bg_color = (100, 100, 255)
            text_color = (255, 255, 255)
        else:
            bg_color = (50, 50, 200)
            text_color = (255, 255, 255)

        # Draw button with border
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=10)

        # Draw text
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

        # Add lock icon if button is locked
        if self.locked:
            lock_text = font.render("🔒", True, (255, 255, 255))
            lock_rect = lock_text.get_rect(
                center=(self.rect.right - 20, self.rect.y + 20)
            )
            surface.blit(lock_text, lock_rect)

    def is_hover(self, pos):
        return (
            self.x <= pos[0] <= self.x + self.width
            and self.y <= pos[1] <= self.y + self.height
        )

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            self.hover = self.is_hover(event.pos)
        elif event.type == MOUSEBUTTONDOWN:
            if self.hover and self.action:
                return self.action
        return None
