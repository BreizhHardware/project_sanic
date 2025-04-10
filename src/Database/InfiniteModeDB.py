import sqlite3
import os


class InfiniteModeDB:
    def __init__(self, db_file="game.db"):
        """
        Initialize database connection for infinite game mode points management.

        Args:
            db_file: SQLite database file path.
        """
        os.makedirs(
            os.path.dirname(db_file) if os.path.dirname(db_file) else ".", exist_ok=True
        )
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create required tables if they don't exist."""
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
        """Get all scores from the table."""
        self.cursor.execute("SELECT * FROM InfiniteMode")
        return self.cursor.fetchall()

    def add_score(self, player_name, score):
        """Add a new score to the InfiniteMode."""
        self.cursor.execute(
            "INSERT INTO InfiniteMode (player_name, score) VALUES (?, ?)",
            (player_name, score),
        )
        self.conn.commit()

    def clear_InfiniteModeDB(self):
        """Clear all scores from the InfiniteMode table."""
        try:
            self.cursor.execute("DELETE FROM InfiniteMode")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error clearing InfiniteMode table: {e}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()