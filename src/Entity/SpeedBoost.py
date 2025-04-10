import os
import pygame
import time
from src.Entity.Entity import Entity


class SpeedBoost(Entity):
    """
    A collectible that temporarily increases the player's movement speed
    for 3 seconds when collected.
    """

    def __init__(self, pos, size=(30, 30), color=(0, 0, 255), texturePath=""):
        super().__init__(pos=pos, size=size, color=color, texturePath=texturePath)
        self.collected = False

        # Speed boost properties
        self.boost_factor = 2
        self.boost_duration = 3

        # Create initial surface
        self.surf = pygame.Surface(size, pygame.SRCALPHA)

        # Load and scale texture
        if texturePath:
            try:
                if os.path.exists(texturePath):
                    texture = pygame.image.load(texturePath).convert_alpha()
                    textureSize = (size[0] * 3, size[1] * 3)
                    self.surf = pygame.transform.scale(texture, textureSize)
                else:
                    self.draw_fallback(color, size)
            except Exception as e:
                self.draw_fallback(color, size)
        else:
            self.draw_fallback(color, size)

        # Set rect
        self.rect = self.surf.get_rect()
        self.rect.topleft = pos

        # Animation properties
        self.animation_frame = 0
        self.last_update = 0

    def draw_fallback(self, color, size):
        """Draw a blue lightning bolt as fallback"""
        self.surf.fill((0, 0, 0, 0))

        # Draw a lightning bolt symbol
        width, height = size
        points = [
            (width // 2, 0),
            (width // 4, height // 2),
            (width // 2 - 2, height // 2),
            (width // 3, height),
            (width // 2 + 5, height // 2 + 5),
            (width // 2 + 2, height // 2),
            (3 * width // 4, height // 2),
        ]

        pygame.draw.polygon(self.surf, color, points)

    def update(self):
        """Update the speed boost animation"""
        now = pygame.time.get_ticks()
        if now - self.last_update > 200:
            self.last_update = now
            self.animation_frame = (self.animation_frame + 1) % 4
            # Simple floating animation
            self.rect.y += [-1, 0, 1, 0][self.animation_frame]

    def on_collision(self, player, game_resources):
        """
        Handle speed boost collision with player

        Args:
            player: The player object to apply the boost to
            game_resources: Game resources object containing player speed
        """
        if not self.collected:
            self.collected = True

            # Store original movement speed
            original_ACC = game_resources.ACC

            # Apply boost effect
            game_resources.ACC *= self.boost_factor

            # Set visual feedback
            player.speed_boost_active = True

            # Schedule effect removal
            pygame.time.set_timer(
                pygame.USEREVENT + 3,  # Custom event ID for speed boost expiration
                self.boost_duration * 1000,  # Convert to milliseconds
                1,  # Only trigger once
            )

            # Store reference to restore original speed
            player.active_speed_boost = {
                "original_ACC": original_ACC,
                "boost_object": self,
            }

            # Remove the collectible from display
            self.kill()

            return True
        return False
