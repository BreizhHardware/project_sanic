import sqlite3
import os


class CheckpointDB:
    def __init__(self, db_file="checkpoint.db"):
        """
        Initialize database connection for checkpoint management

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
        """Create required tables if they don't exist"""
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS checkpoints (
            map_name TEXT PRIMARY KEY,
            pos_x REAL,
            pos_y REAL,
            timestamp INTEGER
        )
        """
        )
        self.conn.commit()

    def save_checkpoint(self, map_name, pos_x, pos_y):
        """
        Save or update checkpoint position

        Args:
            map_name: Name of the current map
            pos_x: X coordinate
            pos_y: Y coordinate
        """
        self.cursor.execute(
            "INSERT OR REPLACE INTO checkpoints (map_name, pos_x, pos_y, timestamp) VALUES (?, ?, ?, strftime('%s'))",
            (map_name, pos_x, pos_y),
        )
        self.conn.commit()

    def get_checkpoint(self, map_name):
        """
        Get saved checkpoint position for a map

        Args:
            map_name: Map name to query

        Returns:
            Tuple (x, y) if checkpoint exists, None otherwise
        """
        self.cursor.execute(
            "SELECT pos_x, pos_y FROM checkpoints WHERE map_name = ?", (map_name,)
        )
        result = self.cursor.fetchone()
        return result if result else None

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
