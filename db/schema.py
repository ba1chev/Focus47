from pathlib import Path

from db.connection import Database

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


class SchemaInitializer:
    """Creates tables and seeds a default user on first run."""

    def __init__(self, database: Database) -> None:
        self._database = database

    def initialize(self) -> None:
        schema = SCHEMA_PATH.read_text()
        conn = self._database.connect()
        try:
            conn.executescript(schema)
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
