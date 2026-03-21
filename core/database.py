import sqlite3

class Database:
    def __init__(self, db_path="data/notes.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        query = """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            title BLOB,
            content BLOB,
            category TEXT,
            pinned INTEGER DEFAULT 0,
            created_at TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()