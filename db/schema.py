from db.config import SCHEMA_PATH
from db.connection import Database


class SchemaInitializer:
    """Creates tables and seeds the admin account on first run."""

    def __init__(self, database: Database, admin_name: str = "Admin",
        admin_account: str = "admin", admin_password_hash: str = "",
        admin_color: str = "#6264a7") -> None:
        self._database = database
        self._admin_name = admin_name
        self._admin_account = admin_account
        self._admin_password_hash = admin_password_hash
        self._admin_color = admin_color

    def initialize(self) -> None:
        schema = SCHEMA_PATH.read_text()
        conn = self._database.connect()
        try:
            conn.executescript(schema)
            self._seed_admin(conn)
            conn.commit()
        finally:
            conn.close()

    def _seed_admin(self, conn) -> None:
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM users WHERE role = 'admin'"
        ).fetchone()["c"]
        if count == 0:
            conn.execute(
                "INSERT INTO users (name, account, password_hash, role, color) "
                "VALUES (?, ?, ?, 'admin', ?)",
                (self._admin_name, self._admin_account,
                 self._admin_password_hash, self._admin_color)
            )
