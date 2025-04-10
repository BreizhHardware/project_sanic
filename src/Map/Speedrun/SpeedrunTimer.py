import pygame
import time
import sqlite3
from datetime import timedelta


class SpeedrunTimer:
    def __init__(self, level_id, db_path="game.db"):
        self.level_id = level_id
        self.db_path = db_path
        self.start_time = None
        self.current_time = 0
        self.is_running = False
        self.best_time = self._get_best_time()
        self.color = (0, 255, 0)  # Green by default
        self.font = pygame.font.Font(None, 36)
        self.collected_items = 0
        self.total_items = 0

    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        self.is_running = True

    def stop(self):
        """Stop the timer and return the final time"""
        if self.is_running:
            self.current_time = time.time() - self.start_time
            self.is_running = False
            return self.current_time
        return self.current_time

    def update(self):
        """Update the timer and its color"""
        if self.is_running:
            self.current_time = time.time() - self.start_time
            if self.best_time is not None:
                if self.current_time < self.best_time:
                    self.color = (0, 255, 0)  # Green if ahead
                else:
                    self.color = (255, 0, 0)  # Red if behind

    def save_time(self, collected_items=0, total_items=0):
        """Save the current time in the database"""
        if not self.is_running and self.current_time > 0:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create the table if it doesn't exist
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS speedrun (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_id TEXT NOT NULL,
                time REAL NOT NULL,
                collected_items INTEGER DEFAULT 0,
                total_items INTEGER DEFAULT 0,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            )

            # Insert the new time
            cursor.execute(
                "INSERT INTO speedrun (level_id, time, collected_items, total_items) VALUES (?, ?, ?, ?)",
                (self.level_id, self.current_time, collected_items, total_items),
            )

            conn.commit()
            conn.close()

            # Update the best time
            self.best_time = self._get_best_time()

    def _get_best_time(self):
        """Get the best time for this level from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT MIN(time) FROM speedrun WHERE level_id = ?", (self.level_id,)
            )

            best_time = cursor.fetchone()[0]
            conn.close()

            return best_time
        except (sqlite3.Error, TypeError):
            return None

    def format_time(self, time_value):
        """Format the time in minutes:seconds.milliseconds"""
        if time_value is None:
            return "00:00.000"

        td = timedelta(seconds=time_value)
        minutes, seconds = divmod(td.seconds, 60)
        milliseconds = td.microseconds // 1000
        return f"{minutes:02}:{seconds:02}.{milliseconds:03}"

    def draw(self, surface):
        """Display the timer on the screen"""
        if self.level_id == "NEXT_INFINITE_LEVEL":
            return  # No timer for infinite mode

        formatted_time = self.format_time(self.current_time)
        text = self.font.render(formatted_time, True, self.color)
        surface.blit(text, (20, surface.get_height() - 50))
