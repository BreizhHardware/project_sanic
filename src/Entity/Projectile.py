import pygame
from pygame.math import Vector2 as vec


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, speed, damage, color=(0, 0, 255)):
        super().__init__()

        # Base attributes
        self.pos = vec(pos)
        self.direction = direction.normalize() if direction.length() > 0 else vec(1, 0)
        self.speed = speed
        self.damage = damage

        # Create projectile surface
        self.surf = pygame.Surface((10, 10))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(center=(pos.x, pos.y))

    def update(self, screen_width, screen_height, player=None, camera=None):
        """Move the projectile and check for collisions"""
        # Movement of the projectile
        self.pos += self.direction * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Check if projectile is out of screen
        if camera:
            # Screen position of the projectile = position + camera position
            screen_x = self.pos.x + camera.camera.x
            screen_y = self.pos.y + camera.camera.y

            # Safety margin to avoid killing the projectile too early
            margin = 50

            if (
                screen_x < -margin
                or screen_x > screen_width + margin
                or screen_y < -margin
                or screen_y > screen_height + margin
            ):
                self.kill()

        # Check for collision with player
        if player and self.rect.colliderect(player.rect):
            player.take_damage(self.damage)
            self.kill()
