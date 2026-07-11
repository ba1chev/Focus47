from db.connection import Database

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL,
    color TEXT NOT NULL DEFAULT '#6264a7'
);

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    start       TEXT NOT NULL,
    end         TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'todo',
    priority    TEXT NOT NULL DEFAULT 'medium',
    category    TEXT NOT NULL DEFAULT '',
    color       TEXT NOT NULL DEFAULT '#6264a7',
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL
);
"""


class SchemaInitializer:
    """Creates tables and seeds a default user on first run."""

    def __init__(self, database: Database) -> None:
        self._database = database

    def initialize(self) -> None:
        conn = self._database.connect()
        try:
            conn.executescript(SCHEMA)
            self._seed_default_user(conn)
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _seed_default_user(conn) -> None:
        count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        if count == 0:
            conn.execute(
                "INSERT INTO users (name, color) VALUES (?, ?)",
                ("Me", "#6264a7")
            )
