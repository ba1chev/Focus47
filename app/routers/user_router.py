import sqlite3
from fastapi import APIRouter, Depends

from db.connection import Database
from app.models.users.user_out import UserOut
from app.repositories.user_repository import UserRepository


class UserRouter:
    """Wires user endpoints to a UserRepository backed by the given Database."""

    def __init__(self, database: Database) -> None:
        self._database = database
        self.router = APIRouter(prefix="/api/users", tags=["users"])
        self._register_routes()

    def _get_session(self):
        yield from self._database.session()

    def _register_routes(self) -> None:
        Session = Depends(self._get_session)

        @self.router.get("", response_model=list[UserOut])
        def list_users(conn: sqlite3.Connection = Session):
            return UserRepository(conn).list()
