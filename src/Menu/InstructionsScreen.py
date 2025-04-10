import pygame
import math
from src.Menu.BackgroundManager import BackgroundManager


class InstructionsScreen:
    def __init__(self, game_resources):
        self.game_resources = game_resources
        self.bg_manager = BackgroundManager(game_resources.WIDTH, game_resources.HEIGHT)

        self.title_font = pygame.font.SysFont("Arial", 72)
        self.text_font = pygame.font.SysFont("Arial", 32)

        self.blink_timer = 0
        self.blink_speed = 0.5

    def draw(self, surface):
        self.bg_manager.draw(surface)

        def render_text_with_outline(text, font, text_color, outline_color):
            text_surface = font.render(text, True, text_color)
            outline_surface = font.render(text, True, outline_color)

            w, h = text_surface.get_size()
            outline_surf = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)

            # Dessiner le contour en décalant le texte
            offsets = [
                (1, 1),
                (1, -1),
                (-1, 1),
                (-1, -1),
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
            ]
            for dx, dy in offsets:
                outline_surf.blit(outline_surface, (dx + 1, dy + 1))

            # Dessiner le texte principal au centre
            outline_surf.blit(text_surface, (1, 1))
            return outline_surf

        title_surf = render_text_with_outline(
            "Game control", self.title_font, (255, 255, 255), (0, 0, 0)
        )
        title_rect = title_surf.get_rect(center=(self.game_resources.WIDTH // 2, 100))
        surface.blit(title_surf, title_rect)

        instructions = [
            "Q : Move left",
            "D : Move right",
            "A : Dash",
            "Espace : Jump",
            "V: Attack",
            "Escape : Pause / Menu",
            "Controller : Use the left joystick to move",
            "B: Dash",
            "A: Jump",
            "X: Attack",
            "Y: Pause / Menu",
        ]

        y_offset = 180
        line_spacing = 40

        for line in instructions:
            text_surf = render_text_with_outline(
                line, self.text_font, (255, 255, 255), (0, 0, 0)
            )
            text_rect = text_surf.get_rect(
                center=(self.game_resources.WIDTH // 2, y_offset)
            )
            surface.blit(text_surf, text_rect)
            y_offset += line_spacing

        self.blink_timer += 0.01
        alpha = abs(math.sin(self.blink_timer * self.blink_speed)) * 255

        skip_text = render_text_with_outline(
            "Press any key to continue", self.text_font, (255, 220, 0), (0, 0, 0)
        )
        skip_text.set_alpha(int(alpha))
        skip_rect = skip_text.get_rect(
            center=(self.game_resources.WIDTH // 2, self.game_resources.HEIGHT - 100)
        )
        surface.blit(skip_text, skip_rect)

    def handle_event(self, event):
        if (
            event.type == pygame.KEYDOWN
            or event.type == pygame.MOUSEBUTTONDOWN
            or event.type == pygame.JOYBUTTONDOWN
        ):
            return "menu"
        return None
