import os
import pygame
import time
from src.Entity.Entity import Entity


class JumpBoost(Entity):
    """
    A collectible that temporarily increases the player's jump power
    for 3 seconds when collected.
    """

    def __init__(self, pos, size=(30, 30), color=(0, 255, 0), texturePath=""):
        super().__init__(pos=pos, size=size, color=color, texturePath=texturePath)
        self.collected = False

        # Jump boost properties
        self.boost_factor = 1.5  # 50% increase in jump power
        self.boost_duration = 3  # Duration in seconds

        # Create initial surface
        self.surf = pygame.Surface(size, pygame.SRCALPHA)

        # Load and scale texture
        if texturePath:
            try:
                if os.path.exists(texturePath):
                    texture = pygame.image.load(texturePath).convert_alpha()
                    textureSize = (size[0] * 1.5, size[1] * 1.5)
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
        """Draw a green arrow pointing up as fallback"""
        self.surf.fill((0, 0, 0, 0))

        # Draw an arrow pointing up
        half_width = size[0] // 2
        height = size[1]

        # Arrow head
        head_points = [
            (half_width, 0),
            (half_width - 8, 10),
            (half_width + 8, 10),
        ]

        # Arrow body
        body_rect = pygame.Rect(half_width - 4, 10, 8, height - 10)

        pygame.draw.polygon(self.surf, color, head_points)
        pygame.draw.rect(self.surf, color, body_rect)

    def update(self):
        """Update the jump boost animation"""
        now = pygame.time.get_ticks()
        if now - self.last_update > 200:
            self.last_update = now
            self.animation_frame = (self.animation_frame + 1) % 4
            # Simple floating animation
            self.rect.y += [-1, 0, 1, 0][self.animation_frame]

    def on_collision(self, player):
        """
        Handle jump boost collision with player

        Args:
            player: The player object to apply the boost to
        """
        if not self.collected:
            self.collected = True

            # Store original jump power
            original_jump_power = player.jump_power

            # Apply boost effect
            player.jump_power *= self.boost_factor

            # Set visual feedback
            player.jump_boost_active = True

            # Schedule effect removal
            pygame.time.set_timer(
                pygame.USEREVENT + 2,  # Custom event ID for jump boost expiration
                self.boost_duration * 1000,  # Convert to milliseconds
                1,  # Only trigger once
            )

            # Store reference to restore original jump power
            player.active_jump_boost = {
                "original_power": original_jump_power,
                "boost_object": self,
            }

            # Remove the collectible from display
            self.kill()

            return True
        return False
