import pygame
import os
from pygame.math import Vector2 as vec


class Entity(pygame.sprite.Sprite):
    def __init__(
        self, pos=(0, 0), size=(30, 30), color=(255, 255, 255), texturePath=""
    ):
        super().__init__()
        self.pos = vec(pos)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        # Default surface
        self.surf = pygame.Surface(size)
        self.surf.fill(color)
        self.rect = self.surf.get_rect()
        self.update_rect()
        if os.path.isfile(texturePath):
            try:
                self.surf = pygame.image.load(texturePath).convert_alpha()
                self.surf = pygame.transform.scale(self.surf, size)
                self.rect = self.surf.get_rect()
            except Exception as e:
                print(f"Error loading texture: {e}")
                # Fallback to default color
                self.surf = pygame.Surface(size)
                self.surf.fill(color)
                self.rect = self.surf.get_rect()
        else:
            self.surf.fill(color)
            self.rect = self.surf.get_rect(center=self.pos)

    def update_rect(self):
        """Update rect position based on entity position"""
        self.rect.midbottom = self.pos

    def update(self):
        """Update entity state - to be overridden by child classes"""
        pass

    def move(self):
        """Handle movement - to be overridden by child classes"""
        pass
