import sqlite3
import os


class LeaderboardDB:
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

    def _create_tables(self):
        print("Ensuring the Leaderboard table has the correct schema")
        # Create the table with the correct schema
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
    def get_all(self):
        """
        Get all scores from the table limited at 10 rows

        Returns:
            List of tuples containing player name and score
        """
        self.cursor.execute("SELECT score, date FROM Leaderboard LIMIT 10")
        return self.cursor.fetchall()

    def get_top_3_scores(self):
        """
        Get top 3 scores from the leaderboard

        Returns:
            List of tuples containing player name and score
        """
        self.cursor.execute(
            "SELECT score, date FROM Leaderboard ORDER BY score DESC LIMIT 3"
        )
        return self.cursor.fetchall()

    def add_score(self, player_name, score):
        """
        Add a new score to the InfiniteMode

        Args:
            player_name: Name of the player
            score: Score to be added
        """
        self.cursor.execute(
            "INSERT INTO Leaderboard (player_name, score) VALUES (?, ?)",
            (player_name, score),
        )
        self.conn.commit()

    def clear_leaderboard(self):
        """
        Clear all scores from the leaderboard
        """
        self.cursor.execute("DELETE FROM Leaderboard")
        self.conn.commit()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()