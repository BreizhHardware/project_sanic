from src.Entity.Entity import Entity
import pygame
from pygame.math import Vector2 as vec
from src.Database.CheckpointDB import CheckpointDB


class Checkpoint(Entity):
    def __init__(
        self, pos, size=(50, 50), color=(0, 255, 0), texture_path="", map_name="default"
    ):
        """
        Initialize a checkpoint entity

        Args:
            pos (tuple): Position of the checkpoint (x, y)
            size (tuple): Size of the checkpoint (width, height)
            color (tuple): Default color if no texture is provided
            texture_path (str): Path to the checkpoint texture
            map_name (str): Name of the current map
        """
        super().__init__(pos, size, color, texture_path)
        self.activated = False
        self.map_name = map_name
        self.default_color = color
        self.activated_color = (0, 100, 0)  # Dark green
        self.db = CheckpointDB()

        # Load texture if provided
        if texture_path:
            try:
                self.image = pygame.image.load(texture_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, size)
                self.surf = self.image
            except Exception as e:
                print(f"Error loading checkpoint texture: {e}")
                self.surf = pygame.Surface(size)
                self.surf.fill(color)
        else:
            self.surf = pygame.Surface(size)
            self.surf.fill(color)

        # Set the rect attribute for positioning
        self.rect = self.surf.get_rect(topleft=pos)

    def activate(self):
        """
        Activate the checkpoint if not already activated.
        Save coordinates to database and change color.

        Returns:
            bool: True if newly activated, False if already activated
        """
        if not self.activated:
            self.activated = True
            # Load the new texture
            try:
                self.image = pygame.image.load(
                    "assets/map/checkpoints/checkpoint.png"
                ).convert_alpha()
                self.image = pygame.transform.scale(self.image, self.surf.get_size())
                self.surf = self.image
            except Exception as e:
                print(f"Error loading checkpoint texture: {e}")
                self.surf.fill(self.activated_color)
            # Save checkpoint to database
            self.db.save_checkpoint(self.map_name, self.pos.x, self.pos.y)

            return True
        return False
