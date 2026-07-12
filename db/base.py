from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase

from db.config import DEFAULT_DB_PATH


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model in Focus47."""


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def sqlite_uri(db_path: Path = DEFAULT_DB_PATH) -> str:
    return f"sqlite:///{db_path}"
