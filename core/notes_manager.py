from datetime import datetime

class NotesManager:
    def __init__(self, db, crypto):
        self.db = db
        self.crypto = crypto

    def create_note(self, title, content, category):
        enc_title = self.crypto.encrypt(title)
        enc_content = self.crypto.encrypt(content)

        query = """
        INSERT INTO notes (title, content, category, created_at)
        VALUES (?, ?, ?, ?)
        """
        self.db.conn.execute(query, (
            enc_title,
            enc_content,
            category,
            datetime.now().isoformat()
        ))
        self.db.conn.commit()

    def get_notes(self):
        cursor = self.db.conn.execute("SELECT * FROM notes")
        notes = []

        for row in cursor:
            notes.append({
                "id": row[0],
                "title": self.crypto.decrypt(row[1]),
                "content": self.crypto.decrypt(row[2]),
                "category": row[3],
                "pinned": row[4]
            })

        notes.sort(key=lambda x: x["pinned"], reverse=True)

        return notes

    def delete_note(self, note_id):
        self.db.conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
        self.db.conn.commit()

    def update_note(self, note_id, title, content, category):
        enc_title = self.crypto.encrypt(title)
        enc_content = self.crypto.encrypt(content)

        query = """
        UPDATE notes
        SET title=?, content=?, category=?
        WHERE id=?
        """

        self.db.conn.execute(query, (
            enc_title,
            enc_content,
            category,
            note_id
        ))
        self.db.conn.commit()

    def search_notes(notes, query):
        return [
            n for n in notes
            if query.lower() in n["title"].lower()
            or query.lower() in n["content"].lower()
        ]

    def toggle_pin(self, note_id, current_state):
        new_state = 0 if current_state else 1

        self.db.conn.execute(
            "UPDATE notes SET pinned=? WHERE id=?",
            (new_state, note_id)
        )
        self.db.conn.commit()