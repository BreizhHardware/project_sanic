import pygame
import random
import math


class BackgroundManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.backgrounds = [
            "assets/map/background/forest_bg.jpg",
            "assets/map/background/desert_bg.jpg",
            "assets/map/background/mountain_bg.jpg",
            "assets/map/background/cave_bg.png",
        ]

        self.background_path = random.choice(self.backgrounds)
        self.init_time = pygame.time.get_ticks()

        try:
            # Load the background image
            self.background = pygame.image.load(self.background_path).convert()
            bg_width = width * 3
            bg_height = height * 3
            self.background = pygame.transform.scale(
                self.background, (bg_width, bg_height)
            )
        except Exception as e:
            print(f"Erreur lors du chargement du fond d'écran: {e}")
            self.background = None

    def draw(self, surface):
        if self.background:
            parallax_factor = 0.4
            time_factor = pygame.time.get_ticks() / 1000

            center_x = (self.background.get_width() - surface.get_width()) / 2
            center_y = (self.background.get_height() - surface.get_height()) / 2

            bg_x = -center_x + math.sin(time_factor) * 50 * parallax_factor
            bg_y = -center_y + math.cos(time_factor) * 30 * parallax_factor

            surface.blit(self.background, (bg_x, bg_y))
        else:
            surface.fill((0, 0, 0))
