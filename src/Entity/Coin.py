# src/Entity/Coin.py
import os

from src.Entity.Entity import Entity
import pygame


class Coin(Entity):
    def __init__(self, pos, size=(50, 50), color=(255, 215, 0), texturePath=""):
        super().__init__(pos=pos, size=size, color=color, texturePath=texturePath)
        self.collected = False

        # Create initial surface
        self.surf = pygame.Surface(size, pygame.SRCALPHA)

        # Load and scale the coin texture if provided
        if texturePath:
            try:
                if os.path.exists(texturePath):
                    texture = pygame.image.load(texturePath).convert_alpha()
                    self.surf = pygame.transform.scale(texture, size)
                else:
                    self.draw_fallback(color, size)
            except Exception as e:
                self.draw_fallback(color, size)
        else:
            self.draw_fallback(color, size)

        # Ensure rect is properly set
        self.rect = self.surf.get_rect()
        self.rect.topleft = pos

    def draw_fallback(self, color, size):
        """Draw a yellow circle as fallback"""
        self.surf.fill((0, 0, 0, 0))  # Clear with transparency
        pygame.draw.circle(self.surf, color, (size[0] // 2, size[1] // 2), size[0] // 2)

    def on_collision(self):
        """Handle coin collision with player"""
        if not self.collected:
            self.collected = True
            self.kill()  # This removes the coin from all sprite groups