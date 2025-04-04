from src.Entity.Entity import Entity
import pygame
from pygame.math import Vector2 as vec


class Projectile(Entity):
    def __init__(
        self, pos, direction, speed, damage, color=(0, 0, 255), enemy_proj=False
    ):
        # Appel du constructeur parent avec les paramètres appropriés
        super().__init__(pos=pos, size=(10, 10), color=color)

        # Attributs spécifiques aux projectiles
        self.direction = direction.normalize() if direction.length() > 0 else vec(1, 0)
        self.speed = speed
        self.damage = damage
        self.enemy_proj = enemy_proj

        # Ajustement du rect pour utiliser le centre plutôt que midbottom
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, screen_width, screen_height, player=None, camera=None, enemy=None):
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
        if player and self.rect.colliderect(player.rect) and self.enemy_proj:
            player.take_damage(self.damage)
            self.kill()

        if enemy and self.rect.colliderect(enemy.rect) and not self.enemy_proj:
            enemy.take_damage(self.damage)
            self.kill()

    # Surcharge pour utiliser center au lieu de midbottom
    def update_rect(self):
        """Update rect position based on entity position"""
        self.rect.center = self.pos
