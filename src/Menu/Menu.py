import pygame
import random
import math
from src.Menu.Button import Button


class Menu:
    def __init__(self, game_resources):
        self.game_resources = game_resources
        self.buttons = []
        button_width = 250
        button_height = 60
        button_spacing = 20
        start_y = self.game_resources.HEIGHT // 2 - 100

        self.backgrounds = [
            "assets/map/background/forest_bg.jpg",
            "assets/map/background/desert_bg.jpg",
            "assets/map/background/mountain_bg.jpg",
            "assets/map/background/cave_bg.png",
        ]

        self.background_path = random.choice(self.backgrounds)

        try:
            # Load the background image
            self.background = pygame.image.load(self.background_path).convert()

            bg_width = game_resources.WIDTH * 3
            bg_height = game_resources.HEIGHT * 3
            self.background = pygame.transform.scale(
                self.background, (bg_width, bg_height)
            )
        except Exception as e:
            print(f"Error while loading menu background: {e}")
            self.background = None

        # Create buttons centered horizontally
        self.buttons.append(
            Button(
                "Play",
                self.game_resources.WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "level_select",
            )
        )

        start_y += button_height + button_spacing
        self.buttons.append(
            Button(
                "Play in infinite mode",
                self.game_resources.WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "infinite",
            )
        )

        start_y += button_height + button_spacing
        self.buttons.append(
            Button(
                "Leaderboard",
                self.game_resources.WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "leaderboard",
            )
        )

        start_y += button_height + button_spacing
        self.buttons.append(
            Button(
                "Quit",
                self.game_resources.WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "quit",
            )
        )

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

        # Draw title
        title = pygame.font.SysFont("Arial", 72).render(
            "Sanic and the princess Zeldo", True, (0, 191, 255)
        )
        title_rect = title.get_rect(
            center=(self.game_resources.WIDTH // 2, self.game_resources.HEIGHT // 4)
        )
        surface.blit(title, title_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface, self.game_resources.font)

    def handle_event(self, event):
        for button in self.buttons:
            action = button.handle_event(event)
            if action:
                return action
        return None
