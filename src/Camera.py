# src/Camera.py
import pygame


class Camera:
    def __init__(self, width, height, game_resources):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.game_resources = game_resources

    def update(self, target):
        # Center the target in the camera view
        x = -target.rect.centerx + self.game_resources.WIDTH // 2
        y = -target.rect.centery + self.game_resources.HEIGHT // 2

        # Update camera position
        self.camera = pygame.Rect(x, y, self.width, self.height)
