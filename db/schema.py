from sqlalchemy import select

from db.base import Base
from db.engine import Database
from db.models.user_record import UserRecord
from db.models.task_record import TaskRecord  # noqa: F401
from db.auto_migrate import run_auto_migrations


class SchemaInitializer:
    """Creates tables, applies additive migrations and seeds the admin account."""

    def __init__(self, database: Database, admin_name: str = "Admin",
        admin_account: str = "admin", admin_password_hash: str = "",
        admin_color: str = "#6264a7") -> None:
        self._database = database
        self._admin_name = admin_name
        self._admin_account = admin_account
        self._admin_password_hash = admin_password_hash
        self._admin_color = admin_color

    def initialize(self) -> None:
        Base.metadata.create_all(self._database.engine)
        run_auto_migrations(self._database.engine)
        with self._database.session() as session:
            self._seed_admin(session)
            session.commit()

    def _seed_admin(self, session) -> None:
        existing = session.execute(
            select(UserRecord).where(UserRecord.role == "admin")
        ).first()
        if existing is None:
            session.add(UserRecord(
                name=self._admin_name,
                account=self._admin_account,
                password_hash=self._admin_password_hash,
                role="admin",
                color=self._admin_color
            ))
