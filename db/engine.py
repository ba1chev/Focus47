from typing import Iterator, Optional
from sqlalchemy.engine import Engine
from contextlib import contextmanager
from sqlalchemy import event, create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.base import sqlite_uri


def _sqlite_options() -> dict:
    return {
        "echo": False,
        "future": True,
        "connect_args": {"check_same_thread": False}
    }


class Database:
    """Owns the SQLAlchemy engine and session factory for the Focus47 DB."""

    def __init__(self, database_uri: Optional[str] = None,
        options: Optional[dict] = None) -> None:
        uri = database_uri or sqlite_uri()
        self._engine: Engine = create_engine(uri, **(options or _sqlite_options()))
        if self._engine.dialect.name == "sqlite":
            self._enable_foreign_keys()
        self._session_factory = sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    def _enable_foreign_keys(self) -> None:
        @event.listens_for(self._engine, "connect")
        def _set_pragma(dbapi_connection, _record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.close()

    @property
    def engine(self) -> Engine:
        return self._engine

    def new_session(self) -> Session:
        return self._session_factory()

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
