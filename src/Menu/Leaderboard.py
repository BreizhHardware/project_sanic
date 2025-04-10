import pygame
import sqlite3
import os
from datetime import datetime

from src.Menu.BackgroundManager import BackgroundManager
from src.Menu.Button import Button
from src.Database.LevelDB import LevelDB


class Leaderboard:
    """This class represents the leaderboard menu for the game."""

    def __init__(self, WIDTH, HEIGHT, font, leaderboard_db, db_path="game.db"):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.font = font
        self.db_path = db_path
        self.leaderboard_db = leaderboard_db

        self.levels = self.get_available_levels()
        self.level_tabs = [f"Level {level}" for level in self.levels]

        self.bg_manager = BackgroundManager(WIDTH, HEIGHT)

        # Define the tabs (levels + infinite mode)
        self.tabs = self.level_tabs + ["Infinite mode"]
        self.current_tab = 0

        self.back_button = Button("Back", 20, self.HEIGHT - 70, 120, 50, "menu")

        # Add buttons for each tab
        self.tab_buttons = []
        tab_width = min(150, (self.WIDTH - 100) / len(self.tabs))

        for i, tab_name in enumerate(self.tabs):
            x_pos = 50 + i * tab_width
            self.tab_buttons.append(
                Button(tab_name, x_pos, 80, tab_width, 40, f"tab_{i}")
            )

        self.load_scores()

    def get_available_levels(self):
        """Get the list of available levels from the database."""
        try:
            db = LevelDB()
            levels = db.get_all_unlocked_levels()
            db.close()
            return sorted(set(levels))  # Remove duplicates and sort
        except:
            return [1]

    def load_scores(self):
        """Load scores from the database for each level."""
        self.scores = {}

        # Load scores for each level
        for i, level in enumerate(self.levels):
            self.scores[i] = self.get_level_scores(str(level))

        # Load scores for infinite mode
        try:
            # Get the TOP 10 scores for infinite mode
            all_scores = self.leaderboard_db.get_top_10_scores()

            # Format the scores for display
            formatted_scores = []
            for score, date in all_scores:
                date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%d/%m/%Y")
                formatted_scores.append((formatted_date, score))

            # Assign the formatted scores to the infinite mode tab
            self.scores[len(self.levels)] = formatted_scores
        except Exception as e:
            print(f"Error loading infinite mode scores: {e}")
            self.scores[len(self.levels)] = []

    def get_level_scores(self, level_id):
        """Get the top 10 scores for a specific level from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT time, date, collected_items, total_items 
                FROM speedrun 
                WHERE level_id = ? 
                ORDER BY time ASC 
                LIMIT 10
                """,
                (level_id,),
            )

            results = cursor.fetchall()
            conn.close()

            # Format results
            formatted_results = []
            for time, date, collected, total in results:
                date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%d/%m/%Y")
                formatted_results.append((formatted_date, time, collected, total))

            return formatted_results
        except (sqlite3.Error, Exception) as e:
            print(f"Error loading scores: {e}")
            return []

    def format_time(self, time_value):
        """Format the time in minutes:seconds.milliseconds."""
        from datetime import timedelta

        td = timedelta(seconds=time_value)
        minutes, seconds = divmod(td.seconds, 60)
        milliseconds = int((time_value * 1000) % 1000)
        return f"{minutes:02}:{seconds:02}.{milliseconds:03}"

    def draw(self, surface):
        """Draw the leaderboard on the given surface."""
        # Refresh scores to ensure the latest data is displayed
        self.load_scores()

        self.bg_manager.draw(surface)

        # Draw a semi-transparent panel
        panel_rect = pygame.Rect(self.WIDTH // 2 - 250, 130, 500, self.HEIGHT - 200)
        panel_surface = pygame.Surface(
            (panel_rect.width, panel_rect.height), pygame.SRCALPHA
        )
        panel_surface.fill((10, 10, 40, 180))
        surface.blit(panel_surface, panel_rect)

        title_font = pygame.font.SysFont("Arial", 48, bold=True)
        title = title_font.render("Leaderboard", True, (255, 255, 255))
        title_shadow = title_font.render("Leaderboard", True, (0, 0, 0))

        title_rect = title.get_rect(center=(self.WIDTH // 2, 40))
        shadow_rect = title_shadow.get_rect(center=(self.WIDTH // 2 + 2, 42))
        surface.blit(title_shadow, shadow_rect)
        surface.blit(title, title_rect)

        font = pygame.font.SysFont("Arial", 20)

        # Draw tabs
        for i, button in enumerate(self.tab_buttons):
            if i == self.current_tab:
                # Highlight current tab
                pygame.draw.rect(surface, (100, 100, 255), button.rect)
            button.draw(surface, font)

        # Determine headers and positions based on the current tab
        if self.current_tab == len(self.levels):  # Infinite mode
            headers = ["Rank", "Date", "Score"]
            header_positions = [
                self.WIDTH // 2 - 150,
                self.WIDTH // 2 - 50,
                self.WIDTH // 2 + 100,
            ]
        else:  # Level scores
            headers = ["Rank", "Date", "Time", "Collected"]
            header_positions = [
                self.WIDTH // 2 - 150,
                self.WIDTH // 2 - 100,
                self.WIDTH // 2 + 50,
                self.WIDTH // 2 + 150,
            ]

        y_pos = 200

        # Draw column headers
        for i, header in enumerate(headers):
            header_text = font.render(header, True, (200, 200, 200))
            surface.blit(header_text, (header_positions[i], y_pos - 30))

        # Draw scores
        scores_for_tab = self.scores.get(self.current_tab, [])

        if not scores_for_tab:
            no_scores_text = self.font.render(
                "No time saved for this level", True, (255, 255, 255)
            )
            surface.blit(
                no_scores_text,
                (self.WIDTH // 2 - no_scores_text.get_width() // 2, y_pos + 40),
            )
        else:
            for i, score_data in enumerate(scores_for_tab):
                row_bg = (30, 30, 60, 150) if i % 2 == 0 else (40, 40, 80, 150)
                row_rect = pygame.Rect(self.WIDTH // 2 - 200, y_pos - 5, 400, 30)
                row_surface = pygame.Surface(
                    (row_rect.width, row_rect.height), pygame.SRCALPHA
                )
                row_surface.fill(row_bg)
                surface.blit(row_surface, row_rect)

                # Rank
                rank_text = self.font.render(f"{i + 1}.", True, (255, 255, 255))
                surface.blit(rank_text, (header_positions[0], y_pos))

                if self.current_tab == len(self.levels):  # Infinite mode
                    date, score = score_data
                    # Date
                    date_text = self.font.render(date, True, (255, 255, 255))
                    surface.blit(date_text, (header_positions[1], y_pos))

                    # Score
                    score_text = self.font.render(str(score), True, (255, 255, 255))
                    surface.blit(score_text, (header_positions[2], y_pos))
                else:  # Level scores
                    date, time, collected, total = score_data

                    # Date
                    date_text = self.font.render(date, True, (255, 255, 255))
                    surface.blit(date_text, (header_positions[1], y_pos))

                    # Time
                    time_text = self.font.render(
                        self.format_time(time), True, (255, 255, 255)
                    )
                    surface.blit(time_text, (header_positions[2], y_pos))

                    # Collected items
                    collected_color = (255, 255, 255)
                    if collected == total:
                        collected_color = (0, 255, 0)

                    collected_text = self.font.render(
                        f"{collected}/{total}", True, collected_color
                    )
                    surface.blit(collected_text, (header_positions[3], y_pos))

                y_pos += 40

        self.back_button.draw(surface, font)

    def handle_event(self, event):
        """Handle events for the leaderboard menu."""
        action = self.back_button.handle_event(event)
        if action:
            return action

        for i, button in enumerate(self.tab_buttons):
            action = button.handle_event(event)
            if action and action.startswith("tab_"):
                self.current_tab = int(action.split("_")[1])
        return None

    def refresh_scores(self, previous_level=""):
        """Refresh scores from the database."""
        if previous_level != "LEADERBOARD":
            self.scores = {}

            # Get the list of levels from the directory
            level_dir = "map/levels/"
            try:
                levels = [
                    f.replace(".json", "")
                    for f in os.listdir(level_dir)
                    if f.endswith(".json")
                ]

                # Get the scores for each level
                for level in levels:
                    scores = self.get_level_scores(level)
                    if scores:
                        self.scores[int(level) - 1] = scores
            except Exception as e:
                print(f"Error while refreshing the score: {e}")
