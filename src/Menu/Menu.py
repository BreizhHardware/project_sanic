import pygame
from src.constant import HEIGHT, WIDTH
from src.Menu.Button import Button


class Menu:
    def __init__(self):
        self.buttons = []
        button_width = 250
        button_height = 60
        button_spacing = 20
        start_y = HEIGHT // 2 - 100

        # Create buttons centered horizontally
        self.buttons.append(
            Button(
                "Jouer",
                WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "play",
            )
        )

        start_y += button_height + button_spacing
        self.buttons.append(
            Button(
                "Jouer en mode infini",
                WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "infinite",
            )
        )

        start_y += button_height + button_spacing
        self.buttons.append(
            Button(
                "Classement",
                WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "leaderboard",
            )
        )

        start_y += button_height + button_spacing
        self.buttons.append(
            Button(
                "Quitter",
                WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "quit",
            )
        )

    def draw(self, surface):
        # Draw title
        title = pygame.font.SysFont("Arial", 72).render(
            "Project Sanic", True, (0, 191, 255)
        )
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        surface.blit(title, title_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event):
        for button in self.buttons:
            action = button.handle_event(event)
            if action:
                return action
        return None
