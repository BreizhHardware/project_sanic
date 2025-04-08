import pygame
from src.Menu.Button import Button


class Leaderboard:
    def __init__(self, HEIGHT, WIDTH, font):
        self.HEIGHT = HEIGHT
        self.WIDTH = WIDTH
        self.font = font
        self.tabs = ["Mode Normal", "Mode Infini"]
        self.current_tab = 0
        self.scores = {
            0: [("Player1", 1000), ("Player2", 800), ("Player3", 600)],
            1: [("Player1", 2000), ("Player2", 1500), ("Player3", 1200)],
        }
        self.back_button = Button("Retour", 20, self.HEIGHT - 70, 120, 50, "menu")
        tab_width = 150
        self.tab_buttons = [
            Button(
                self.tabs[0], self.WIDTH // 2 - tab_width, 80, tab_width, 40, "tab_0"
            ),
            Button(self.tabs[1], self.WIDTH // 2, 80, tab_width, 40, "tab_1"),
        ]

    def draw(self, surface):
        # Draw title
        title = pygame.font.SysFont("Arial", 48).render(
            "Classement", True, (0, 191, 255)
        )
        title_rect = title.get_rect(center=(self.WIDTH // 2, 40))
        surface.blit(title, title_rect)

        font = pygame.font.SysFont("Arial", 20)

        # Draw tabs
        for i, button in enumerate(self.tab_buttons):
            if i == self.current_tab:
                pygame.draw.rect(
                    surface,
                    (100, 149, 237),
                    (button.x, button.y, button.width, button.height),
                )
            button.draw(surface, font)

        # Draw scores
        y_pos = 150
        for i, (name, score) in enumerate(self.scores[self.current_tab]):
            rank_text = self.font.render(
                f"{i+1}. {name}: {score}", True, (255, 255, 255)
            )
            surface.blit(
                rank_text, (self.WIDTH // 2 - rank_text.get_width() // 2, y_pos)
            )
            y_pos += 40

        self.back_button.draw(surface, font)

    def handle_event(self, event):
        action = self.back_button.handle_event(event)
        if action:
            return action

        for i, button in enumerate(self.tab_buttons):
            action = button.handle_event(event)
            if action and action.startswith("tab_"):
                self.current_tab = int(action.split("_")[1])
        return None
