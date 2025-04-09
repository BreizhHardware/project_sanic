import sqlite3
import os


class InfiniteModeDB:
    def __init__(self, db_file="game.db"):
        """
        Initialize database connection for infinite game mode points management

        Args:
            db_file: SQLite database file path
        """
        # Create database directory if it doesn't exist
        os.makedirs(
            os.path.dirname(db_file) if os.path.dirname(db_file) else ".", exist_ok=True
        )

        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self.clear_InfiniteModeDB()

    def _create_tables(self):
        print("Creating infinite mode table if it doesn't exist")
        """Create required tables if they don't exist"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS InfiniteMode (
            player_name TEXT,
            score INTEGER
            )
            """
        )
        self.conn.commit()
    def get_all(self):
        """
        Get all scores from the table

        Returns:
            List of tuples containing player name and score
        """
        self.cursor.execute("SELECT * FROM InfiniteMode")
        return self.cursor.fetchall()

    def add_score(self, player_name, score):
        """
        Add a new score to the InfiniteMode

        Args:
            player_name: Name of the player
            score: Score to be added
        """
        self.cursor.execute(
            "INSERT INTO InfiniteMode (player_name, score) VALUES (?, ?)",
            (player_name, score),
        )
        self.conn.commit()

    def clear_InfiniteModeDB(self):
        """
        Clear all scores from the leaderboard
        """
        self.cursor.execute("DELETE FROM InfiniteMode")
        self.conn.commit()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()