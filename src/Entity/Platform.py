import pygame
from src.Entity.Entity import Entity


class Platform(Entity):
    def __init__(
        self,
        width,
        height,
        x,
        y,
        color=(255, 0, 0),
        texturePath="",
        is_moving=False,
        movement_type="",
        movement_points=[{"x": 0, "y": 0}, {"x": 0, "y": 0}],
        movement_speed=0,
        wait_time=0,
    ):
        super().__init__(
            pos=(x, y), size=(width, height), color=color, texturePath=texturePath
        )
        # Override rect setting for platforms if needed
        self.rect = self.surf.get_rect(center=(x, y))

        self.is_moving = is_moving
        self.movement_type = movement_type
        self.movement_points = movement_points
        self.movement_speed = movement_speed
        self.wait_time = wait_time
        self.coeff = -1

    def move_linear(self, dir, movement_points, movement_speed, wait_time, coeff):
        if not dir:
            if (self.rect.y <= movement_points[0]["y"]) or (
                self.coeff == 1 and not self.rect.y >= movement_points[1]["y"]
            ):
                a = 1

            if (self.rect.y >= movement_points[1]["y"]) or (
                self.coeff == -1 and not self.rect.y <= movement_points[0]["y"]
            ):
                a = -1
            self.rect.y += a * movement_speed
            self.coeff = a
