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

    def activate(self):
        """
        Activate the checkpoint if not already activated.
        Save coordinates to database and change color.

        Returns:
            bool: True if newly activated, False if already activated
        """
        if not self.activated:
            self.activated = True
            # Change color to dark green
            if not hasattr(self, "original_surf"):
                self.original_surf = self.surf.copy()
            self.surf.fill(self.activated_color)
            # Save checkpoint to database
            self.db.save_checkpoint(self.map_name, self.pos.x, self.pos.y)

            return True
        return False
