import sqlite3

from app.models.enums.role import Role


class UserRepository:
    """Data-access for users against a SQLite connection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def list(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT id, name, account, role, color FROM users ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]

    def get(self, user_id: int) -> dict | None:
        row = self._conn.execute(
            "SELECT id, name, account, role, color FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_by_account(self, account: str) -> dict | None:
        row = self._conn.execute(
            "SELECT id, name, account, role, color, password_hash "
            "FROM users WHERE account = ?",
            (account,)
        ).fetchone()
        return dict(row) if row else None

    def create(self, name: str, account: str, password_hash: str,
        role: Role = Role.REGULAR, color: str = "#6264a7") -> dict:
        cursor = self._conn.execute(
            "INSERT INTO users (name, account, password_hash, role, color) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, account, password_hash, role.value, color)
        )
        self._conn.commit()
        return self.get(cursor.lastrowid)
