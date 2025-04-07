import sqlite3
import os


class LevelDB:
    def __init__(self, db_file="game.db"):
        """
        Initialize database connection for level progression management

        Args:
            db_file: SQLite database file path
        """
        # Create database directory if it doesn't exist
        os.makedirs(
            os.path.dirname(db_file) if os.path.dirname(db_file) else ".", exist_ok=True
        )

        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_unlocked_levels_table()

    def create_unlocked_levels_table(self):
        """Create the table to store unlocked levels if it doesn't exist"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS unlocked_levels (
                level_number INTEGER PRIMARY KEY,
                unlocked INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT (strftime('%s'))
            )
        """
        )
        self.connection.commit()

    def is_level_unlocked(self, level_number):
        """
        Check if a specific level is unlocked

        Args:
            level_number: Level number to check

        Returns:
            bool: True if level is unlocked, False otherwise
        """
        # Level 1 is always unlocked
        if level_number == 1:
            return True

        self.cursor.execute(
            "SELECT unlocked FROM unlocked_levels WHERE level_number = ?",
            (level_number,),
        )
        result = self.cursor.fetchone()
        return bool(result and result[0])

    def unlock_level(self, level_number):
        """
        Unlock a specific level

        Args:
            level_number: Level number to unlock
        """
        self.cursor.execute(
            "INSERT OR REPLACE INTO unlocked_levels (level_number, unlocked) VALUES (?, 1)",
            (level_number,),
        )
        self.connection.commit()

    def get_all_unlocked_levels(self):
        """
        Get a list of all unlocked level numbers

        Returns:
            list: List of unlocked level numbers
        """
        self.cursor.execute(
            "SELECT level_number FROM unlocked_levels WHERE unlocked = 1"
        )
        return [1] + [
            row[0] for row in self.cursor.fetchall()
        ]  # Level 1 + all unlocked levels

    def reset_progress(self):
        """
        Reset all progress, keeping only level 1 unlocked
        """
        try:
            self.cursor.execute("DELETE FROM unlocked_levels")
            self.connection.commit()
            self.unlock_level(1)  # Always unlock level 1
        except Exception as e:
            print(f"Error resetting level progress: {e}")

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
