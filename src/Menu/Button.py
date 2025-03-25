from pygame.locals import *
import pygame
from src.constant import font


class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action
        self.hover = False

    def draw(self, surface):
        # Button colors
        color = (100, 149, 237) if self.hover else (65, 105, 225)
        border_color = (255, 255, 255)

        # Draw button with border
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(
            surface, border_color, (self.x, self.y, self.width, self.height), 2
        )

        # Draw text
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(
            center=(self.x + self.width / 2, self.y + self.height / 2)
        )
        surface.blit(text_surf, text_rect)

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
