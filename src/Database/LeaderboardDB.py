import sqlite3
import os


class LeaderboardDB:
    def __init__(self, db_file="game.db"):
        """
        Initialize database connection for leaderboard management.

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
        """Ensure the Leaderboard table has the correct schema."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Leaderboard (
            player_name TEXT,
            score INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def get_top_10_scores(self):
        """Get top 10 scores from the leaderboard."""
        self.cursor.execute(
            "SELECT score, date FROM Leaderboard ORDER BY score DESC LIMIT 10"
        )
        return self.cursor.fetchall()

    def add_score(self, player_name, score):
        """Add a new score to the leaderboard."""
        self.cursor.execute(
            "INSERT INTO Leaderboard (player_name, score) VALUES (?, ?)",
            (player_name, score),
        )
        self.conn.commit()

    def clear_leaderboard(self):
        """Clear all scores from the leaderboard."""
        self.cursor.execute("DELETE FROM Leaderboard")
        self.conn.commit()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()