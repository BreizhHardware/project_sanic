# src/Camera.py
import pygame
from src.constant import WIDTH, HEIGHT


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def update(self, target):
        # Center the target in the camera view
        x = -target.rect.centerx + WIDTH // 2
        y = -target.rect.centery + HEIGHT // 2

        # Update camera position
        self.camera = pygame.Rect(x, y, self.width, self.height)
