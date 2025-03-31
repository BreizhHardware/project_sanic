import pygame
from src.Entity.Entity import Entity


class Exit(Entity):
    """
    Class representing a level exit/goal point that triggers level completion when touched.
    Inherits from Entity base class.
    """

    def __init__(self, x, y, width, height, next_level, sprite_path=None):
        """
        Initialize the exit object.

        Args:
            x (int): X-coordinate position
            y (int): Y-coordinate position
            width (int): Width of the exit
            height (int): Height of the exit
            next_level (str): ID or name of the level to load when exiting
            sprite_path (str, optional): Path to the sprite image for the exit
        """
        super().__init__(pos=(x, y), size=(width, height), color=(0, 255, 0))
        self.next_level = next_level  # Store the next level to load
        self.active = True  # Flag to prevent multiple triggers
        self.player = None  # Will store the player reference

        # Load sprite if provided
        if sprite_path:
            try:
                self.image = pygame.image.load(sprite_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
                self.surf = self.image
            except Exception as e:
                print(f"Error loading exit sprite: {e}")

    def set_player(self, player):
        """
        Set the player reference for collision detection.

        Args:
            player: The player entity to check collision with
        """
        self.player = player

    def update(self):
        """
        Check for collision with the player and trigger level completion.
        """
        # Skip collision check if player reference is not set
        if not self.player or not self.active:
            return

        # Check if player is colliding with exit
        if self.rect.colliderect(self.player.rect):
            # Create and post a level complete event
            exit_event = pygame.event.Event(
                pygame.USEREVENT,
                {"action": "level_complete", "next_level": self.next_level},
            )
            pygame.event.post(exit_event)
            self.active = False  # Prevent multiple triggers
