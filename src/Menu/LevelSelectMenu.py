import pygame
import os
import re

from src.Database.LevelDB import LevelDB
from src.Menu.Button import Button
from src.game import clear_checkpoint_database


class LevelSelectMenu:
    """
    A menu for selecting game levels loaded from JSON files.
    Presents all available levels from the map/levels/ directory as buttons.
    """

    def __init__(self, game_resources):
        """
        Initialize the level selection menu.

        Args:
            game_resources: GameResources object containing game settings and resources
        """
        self.game_resources = game_resources
        self.buttons = []
        self.levels = []

        # Button dimensions
        self.button_width = 250
        self.button_height = 60
        self.button_spacing = 20

        # Initialize database and get unlocked levels
        self.db = LevelDB()
        self.db.create_unlocked_levels_table()
        self.unlocked_levels = self.db.get_all_unlocked_levels()

        # Scan for level files
        self._scan_levels()

        # Generate level buttons
        self._create_buttons()

        # Add back button and reset progress button
        self._add_navigation_buttons()

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
        Create buttons for each available level.
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

            # Check if level is unlocked
            is_unlocked = self.db.is_level_unlocked(level_num)
            button_text = f"Level {level_num}"
            button_color = None

            # If locked, disable button functionality
            action = (
                {"action": "select_level", "level_file": level_file}
                if is_unlocked
                else None
            )

            # Create button
            self.buttons.append(
                Button(
                    button_text,
                    x,
                    y,
                    self.button_width,
                    self.button_height,
                    action,
                    locked=not is_unlocked,
                )
            )

    def _add_navigation_buttons(self):
        """
        Add navigation buttons (back and reset progress).
        """
        # Back button
        self.buttons.append(
            Button(
                "Back",
                self.game_resources.WIDTH // 4 - self.button_width // 2,
                self.game_resources.HEIGHT - 100,
                self.button_width,
                self.button_height,
                "back_to_main",
            )
        )

        # Reset progress button
        self.buttons.append(
            Button(
                "Reset Progress",
                3 * self.game_resources.WIDTH // 4 - self.button_width // 2,
                self.game_resources.HEIGHT - 100,
                self.button_width,
                self.button_height,
                "reset_progress",
            )
        )

    def draw(self, surface):
        """
        Draw the level selection menu.

        Args:
            surface: Pygame surface to draw on
        """
        # Draw title
        title = pygame.font.SysFont("Arial", 48).render(
            "Select Level", True, (0, 191, 255)
        )
        title_rect = title.get_rect(
            center=(self.game_resources.WIDTH // 2, self.game_resources.HEIGHT // 6)
        )
        surface.blit(title, title_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface, self.game_resources.font)

        # Display message if no levels found
        if not self.levels:
            no_levels = pygame.font.SysFont("Arial", 32).render(
                "No levels found", True, (255, 0, 0)
            )
            no_levels_rect = no_levels.get_rect(
                center=(self.game_resources.WIDTH // 2, self.game_resources.HEIGHT // 2)
            )
            surface.blit(no_levels, no_levels_rect)

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
                if action == "reset_progress":
                    # Clear checkpoint database
                    clear_checkpoint_database()
                    return None  # Stay in the level select menu
                return action
        return None
