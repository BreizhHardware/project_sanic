import pygame
from src.Entity.Entity import Entity
from src.constant import WIDTH, HEIGHT


class Platform(Entity):
    def __init__(self, width, height, x, y, color=(255, 0, 0)):
        super().__init__(pos=(x, y), size=(width, height), color=color)
        # Override rect setting for platforms if needed
        self.rect = self.surf.get_rect(center=(x, y))
