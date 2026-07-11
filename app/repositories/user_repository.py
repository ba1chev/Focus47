import sqlite3

from app.models.users.user_create import UserCreate


class UserRepository:
    """Data-access for users against a SQLite connection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def list(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT id, name, color FROM users ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]

    def get(self, user_id: int) -> dict | None:
        row = self._conn.execute(
            "SELECT id, name, color FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None

    def create(self, user: UserCreate) -> dict:
        cursor = self._conn.execute(
            "INSERT INTO users (name, color) VALUES (?, ?)",
            (user.name, user.color)
        )
        self._conn.commit()
        return self.get(cursor.lastrowid)
