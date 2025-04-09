import pygame
import random
import math

from src.Menu.BackgroundManager import BackgroundManager
from src.Menu.Button import Button


class Menu:
    def __init__(self, game_resources):
        self.game_resources = game_resources
        self.buttons = []
        button_width = 250
        button_height = 60
        button_spacing = 20
        start_y = self.game_resources.HEIGHT // 2 - 100

        self.bg_manager = BackgroundManager(game_resources.WIDTH, game_resources.HEIGHT)

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
        self.bg_manager.draw(surface)

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
