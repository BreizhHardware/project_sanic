import pygame
from src.Entity.Entity import Entity


class Platform(Entity):
    def __init__(self, width, height, x, y, color=(255, 0, 0), texturePath=""):
        super().__init__(
            pos=(x, y), size=(width, height), color=color, texturePath=texturePath
        )
        # Override rect setting for platforms if needed
        self.rect = self.surf.get_rect(center=(x, y))
