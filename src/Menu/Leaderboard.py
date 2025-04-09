import pygame
import sqlite3
from datetime import datetime
from src.Menu.Button import Button
from src.Database.LevelDB import LevelDB


class Leaderboard:
    """This class represents the leaderboard menu for the game."""

    def __init__(self, WIDTH, HEIGHT, font, db_path="game.db"):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.font = font
        self.db_path = db_path

        self.levels = self.get_available_levels()
        self.level_tabs = [f"Level {level}" for level in self.levels]

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
            return sorted(levels)
        except:
            return [1]

    def load_scores(self):
        """Load scores from the database for each level."""
        self.scores = {}

        # Load scores for each level
        for i, level in enumerate(self.levels):
            self.scores[i] = self.get_level_scores(str(level))

        # TO DO: Load scores for infinite mode
        self.scores[len(self.levels)] = []

    def get_level_scores(self, level_id):
        """Get the top 10 scores for a specific level from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT time, date 
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
            for time, date in results:
                date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%d/%m/%Y")
                formatted_results.append((formatted_date, time))

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
        title = pygame.font.SysFont("Arial", 48).render(
            "Classement", True, (0, 191, 255)
        )
        title_rect = title.get_rect(center=(self.WIDTH // 2, 40))
        surface.blit(title, title_rect)

        font = pygame.font.SysFont("Arial", 20)

        # Draw tabs
        for i, button in enumerate(self.tab_buttons):
            if i == self.current_tab:
                # Highlight current tab
                pygame.draw.rect(surface, (100, 100, 255), button.rect)
            button.draw(surface, font)

        # Draw scores
        y_pos = 150
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
            for i, (date, time) in enumerate(scores_for_tab):

                rank_text = self.font.render(f"{i+1}.", True, (255, 255, 255))
                surface.blit(rank_text, (self.WIDTH // 2 - 150, y_pos))

                date_text = self.font.render(date, True, (255, 255, 255))
                surface.blit(date_text, (self.WIDTH // 2 - 100, y_pos))

                time_text = self.font.render(
                    self.format_time(time), True, (255, 255, 255)
                )
                surface.blit(time_text, (self.WIDTH // 2 + 50, y_pos))

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
