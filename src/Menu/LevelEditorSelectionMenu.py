import pygame
import os
import re

from src.Menu.BackgroundManager import BackgroundManager
from src.Menu.Button import Button


class LevelEditorSelectionMenu:
    """
    A menu for selecting an existing level to edit or creating a new level.
    """

    def __init__(self, game_resources):
        """
        Initialize the level editor selection menu.

        Args:
            game_resources: GameResources object containing game settings and resources
        """
        self.game_resources = game_resources
        self.buttons = []
        self.levels = []

        self.bg_manager = BackgroundManager(game_resources.WIDTH, game_resources.HEIGHT)

        # Button dimensions
        self.button_width = 250
        self.button_height = 60
        self.button_spacing = 20

        # Scan for level files
        self._scan_levels()

        # Generate level buttons
        self._create_buttons()

    def _scan_levels(self):
        """
        Scan the levels directory for JSON level files and sort them numerically.
        """
        try:
            # Get all JSON files in the levels directory
            level_dir = "map/levels/"
            if not os.path.exists(level_dir):
                os.makedirs(level_dir)  # Create directory if it doesn't exist

            files = [f for f in os.listdir(level_dir) if f.endswith(".json")]

            # Extract level numbers using regex and sort numerically
            level_pattern = re.compile(r"(\d+)\.json$")
            self.levels = []

            for file in files:
                match = level_pattern.search(file)
                if match:
                    level_number = int(match.group(1))
                    self.levels.append((level_number, f"{level_dir}{file}"))

            # Sort levels by number
            self.levels.sort(key=lambda x: x[0])

        except Exception as e:
            print(f"Error scanning levels: {e}")
            self.levels = []

    def _create_buttons(self):
        """
        Create buttons for each available level and new level button.
        """
        # Calculate how many buttons can fit per row
        buttons_per_row = 3
        button_width_with_spacing = self.button_width + self.button_spacing

        # Start position for the grid of buttons
        start_x = (
            self.game_resources.WIDTH
            - (button_width_with_spacing * min(buttons_per_row, len(self.levels) or 1))
        ) // 2
        start_y = self.game_resources.HEIGHT // 3

        # Create buttons for each level
        for i, (level_num, level_file) in enumerate(self.levels):
            # Calculate position in grid
            row = i // buttons_per_row
            col = i % buttons_per_row

            x = start_x + (col * button_width_with_spacing)
            y = start_y + (row * (self.button_height + self.button_spacing))

            # Create button
            self.buttons.append(
                Button(
                    f"Edit Level {level_num}",
                    x,
                    y,
                    self.button_width,
                    self.button_height,
                    {"action": "edit_level", "level_file": level_file},
                )
            )

        # Add "Create New Level" button
        new_level_y = start_y + ((len(self.levels) // buttons_per_row) + 1) * (
            self.button_height + self.button_spacing
        )
        self.buttons.append(
            Button(
                "Create New Level",
                self.game_resources.WIDTH // 2 - self.button_width // 2,
                new_level_y,
                self.button_width,
                self.button_height,
                {"action": "new_level"},
            )
        )

        # Add Back button
        self.buttons.append(
            Button(
                "Back",
                self.game_resources.WIDTH // 2 - self.button_width // 2,
                self.game_resources.HEIGHT - 100,
                self.button_width,
                self.button_height,
                "back_to_levels",
            )
        )

    def draw(self, surface):
        """
        Draw the level selection menu.

        Args:
            surface: Pygame surface to draw on
        """
        self.bg_manager.draw(surface)
        # Draw title
        title = pygame.font.SysFont("Arial", 48).render(
            "Level Editor", True, (0, 191, 255)
        )
        title_rect = title.get_rect(
            center=(self.game_resources.WIDTH // 2, self.game_resources.HEIGHT // 6)
        )
        surface.blit(title, title_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface, self.game_resources.font)

    def handle_event(self, event):
        """
        Handle user input events.

        Args:
            event: Pygame event to process

        Returns:
            dict/str/None: Action to perform based on button clicked, or None
        """
        for button in self.buttons:
            action = button.handle_event(event)
            if action:
                return action
        return None
