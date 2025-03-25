import pygame
from pygame.locals import *
from src.pygame_basics import WIDTH, HEIGHT, font


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


class Leaderboard:
    def __init__(self):
        self.tabs = ["Mode Normal", "Mode Infini"]
        self.current_tab = 0
        self.scores = {
            0: [("Player1", 1000), ("Player2", 800), ("Player3", 600)],
            1: [("Player1", 2000), ("Player2", 1500), ("Player3", 1200)],
        }
        self.back_button = Button("Retour", 20, HEIGHT - 70, 120, 50, "menu")
        tab_width = 150
        self.tab_buttons = [
            Button(self.tabs[0], WIDTH // 2 - tab_width, 80, tab_width, 40, "tab_0"),
            Button(self.tabs[1], WIDTH // 2, 80, tab_width, 40, "tab_1"),
        ]

    def draw(self, surface):
        # Draw title
        title = pygame.font.SysFont("Arial", 48).render(
            "Classement", True, (0, 191, 255)
        )
        title_rect = title.get_rect(center=(WIDTH // 2, 40))
        surface.blit(title, title_rect)

        # Draw tabs
        for i, button in enumerate(self.tab_buttons):
            if i == self.current_tab:
                pygame.draw.rect(
                    surface,
                    (100, 149, 237),
                    (button.x, button.y, button.width, button.height),
                )
            button.draw(surface)

        # Draw scores
        y_pos = 150
        for i, (name, score) in enumerate(self.scores[self.current_tab]):
            rank_text = font.render(f"{i+1}. {name}: {score}", True, (255, 255, 255))
            surface.blit(rank_text, (WIDTH // 2 - rank_text.get_width() // 2, y_pos))
            y_pos += 40

        self.back_button.draw(surface)

    def handle_event(self, event):
        action = self.back_button.handle_event(event)
        if action:
            return action

        for i, button in enumerate(self.tab_buttons):
            action = button.handle_event(event)
            if action and action.startswith("tab_"):
                self.current_tab = int(action.split("_")[1])
        return None


class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action
        self.hover = False

    def draw(self, surface):
        # Button colors
        color = (100, 149, 237) if self.hover else (65, 105, 225)
        border_color = (255, 255, 255)

        # Draw button with border
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(
            surface, border_color, (self.x, self.y, self.width, self.height), 2
        )

        # Draw text
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(
            center=(self.x + self.width / 2, self.y + self.height / 2)
        )
        surface.blit(text_surf, text_rect)

    def is_hover(self, pos):
        return (
            self.x <= pos[0] <= self.x + self.width
            and self.y <= pos[1] <= self.y + self.height
        )

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            self.hover = self.is_hover(event.pos)
        elif event.type == MOUSEBUTTONDOWN:
            if self.hover and self.action:
                return self.action
        return None
