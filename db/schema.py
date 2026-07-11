from pathlib import Path

from db.connection import Database

SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "schema.sql"


class SchemaInitializer:
    """Creates tables and seeds a default user on first run."""

    def __init__(self, database: Database,
        default_user_name: str = "Me", default_user_color: str = "#6264a7") -> None:
        self._database = database
        self._default_user_name = default_user_name
        self._default_user_color = default_user_color

    def initialize(self) -> None:
        schema = SCHEMA_PATH.read_text()
        conn = self._database.connect()
        try:
            conn.executescript(schema)
            self._seed_default_user(conn)
            conn.commit()
        finally:
            conn.close()

    def _seed_default_user(self, conn) -> None:
        count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        if count == 0:
            conn.execute(
                "INSERT INTO users (name, color) VALUES (?, ?)",
                (self._default_user_name, self._default_user_color)
            )
