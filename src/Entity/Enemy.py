import pygame
import os
from PIL import Image, ImageSequence
import random
from src.Entity.Entity import Entity
from pygame.math import Vector2 as vec
from src.Entity.Projectile import Projectile


class Enemy(Entity):
    def __init__(self, enemy_data):
        self.size = enemy_data.get("size", [50, 50])
        super().__init__(self.size)

        # Base attributes
        self.enemy_type = enemy_data.get("type", "turret")
        self.health = enemy_data.get("health", 1)
        self.damage = enemy_data.get("damage", 1)
        self.behavior = enemy_data.get("behavior", "stationary")
        self.speed = enemy_data.get("speed", 1.5)

        # Initial position
        self.pos = vec(enemy_data.get("x", 0), enemy_data.get("y", 0))

        # Animation attributes
        self.frames = []
        self.current_frame = 0
        self.animation_speed = enemy_data.get("animation_speed", 0.1)
        self.animation_timer = 0

        sprite_path = enemy_data.get("sprite_sheet", "assets/enemy/default_enemy.png")

        # Load sprite sheet or GIF depending on enemy type and file extension
        if sprite_path.lower().endswith(".gif") and self.enemy_type == "turret":
            self.load_gif_frames(sprite_path)
            if self.frames:
                self.surf = self.frames[0]
            else:
                # Default sprite
                self.surf = pygame.Surface((40, 40))
                self.surf.fill((255, 0, 0))
        else:
            try:
                self.surf = pygame.image.load(sprite_path).convert_alpha()
                self.surf = pygame.transform.scale(self.surf, self.size)
            except:
                # Default sprite
                self.surf = pygame.Surface((40, 40))
                self.surf.fill((255, 0, 0))

        # Initial rectangle
        self.rect = self.surf.get_rect(center=(self.pos.x, self.pos.y))

        # Comportement variable
        self.current_patrol_point = 0
        self.patrol_points = enemy_data.get("patrol_points", [])
        self.detection_radius = enemy_data.get("detection_radius", 200)
        self.attack_interval = enemy_data.get("attack_interval", 0.3)
        self.attack_range = enemy_data.get("attack_range", 300)
        self.attack_timer = 0
        self.direction = 1  # 1 = right, -1 = left

        # State variables
        self.is_attacking = False
        self.detected_player = False

    def load_gif_frames(self, gif_path):
        """Load frames from a GIF file"""
        try:
            gif = Image.open(gif_path)
            frame_count = 0

            for frame in ImageSequence.Iterator(gif):
                frame_surface = pygame.image.fromstring(
                    frame.convert("RGBA").tobytes(), frame.size, "RGBA"
                )
                frame_surface = pygame.transform.scale(frame_surface, (80, 80))
                self.frames.append(frame_surface)
                frame_count += 1

            print(f"Chargé {frame_count} frames depuis {gif_path}")
        except Exception as e:
            print(f"Erreur lors du chargement du GIF: {e}")
            self.frames = []

    def update(self, player=None, dt=1 / 60):
        """Updates enemy's status and position"""
        if player:
            self.check_collision_with_player(player)

        if self.behavior == "patrol" and self.patrol_points:
            self.patrol()
        elif self.behavior == "chase" and player:
            self.chase(player)
        elif self.behavior == "stationary" and player:
            self.stationary_attack(player)

        # Animation management for turret enemies
        if self.enemy_type == "turret" and self.frames:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.surf = self.frames[self.current_frame]

        # Update rect position based on entity position
        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y

    def patrol(self):
        """Patrol behavior between defined coordinates"""
        if not self.patrol_points:
            return

        target = self.patrol_points[self.current_patrol_point]
        target_pos = vec(target["x"], target["y"])

        direction = target_pos - self.pos
        if direction.length() < self.speed:
            # Patrol point reached, go to the next one
            self.current_patrol_point = (self.current_patrol_point + 1) % len(
                self.patrol_points
            )
        else:
            direction = direction.normalize() * self.speed
            self.pos += direction
            self.direction = 1 if direction.x > 0 else -1

    def chase(self, player):
        """Chase player when in range"""
        distance_to_player = vec(
            player.pos.x - self.pos.x, player.pos.y - self.pos.y
        ).length()

        if distance_to_player <= self.detection_radius:
            self.detected_player = True
            direction = vec(player.pos.x - self.pos.x, player.pos.y - self.pos.y)

            if direction.length() > 0:
                direction = direction.normalize() * self.speed
                self.pos += direction
                self.direction = 1 if direction.x > 0 else -1
        else:
            self.detected_player = False

    def stationary_attack(self, player, FPS=60):
        """Remote attack for turret-like enemies"""
        distance_to_player = vec(
            player.pos.x - self.pos.x, player.pos.y - self.pos.y
        ).length()

        if distance_to_player <= self.attack_range:
            self.attack_timer += 1 / FPS

            if self.attack_timer >= self.attack_interval:
                self.attack_timer = 0
                self.attack(player)

    def attack(self, player):
        """Do an attack action on the player"""
        self.is_attacking = True

        # For turret-type enemies, create a projectile
        if self.enemy_type == "turret":
            # Calculate direction to player
            direction = vec(player.pos.x - self.pos.x, player.pos.y - self.pos.y)

            projectile = Projectile(
                pos=vec(self.pos.x, self.pos.y),
                direction=direction,
                speed=self.speed,
                damage=self.damage,
                enemy_proj=True,
                texturePath="assets/map/enemy/Laser.png",
                size=(50, 10),
            )

            # Add projectile to the sprite group (to be placed in main.py)
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {"action": "create_projectile", "projectile": projectile},
                )
            )

    def take_damage(self, amount, player):
        """Deal damage to the enemy and check if it should be destroyed"""
        self.health -= amount
        if self.health <= 0:
            self.kill()
            if random.random() < 0.3:
                pygame.event.post(
                    pygame.event.Event(
                        pygame.USEREVENT,
                        {"action": "add_projectiles"}
                    )
                )
                player.add_projectiles()
            return True
        return False

    def check_collision_with_player(self, player):
        """Check collision with player and apply damage or knockback"""
        if self.rect.colliderect(player.rect):
            # Colide on top
            if player.rect.bottom <= self.rect.top + 10 and player.vel.y > 0:
                # Enemy takes damage
                self.take_damage(1, player)
                # Player bump
                player.vel.y = -15
            else:
                # Enemy deals damage to player
                player.take_damage(self.damage)
                # KB LOL MINECRAFT
                knockback_direction = 1 if player.pos.x > self.pos.x else -1
                player.vel.x = knockback_direction * 8