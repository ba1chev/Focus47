import sqlite3
from fastapi import APIRouter, Depends, HTTPException

from db.connection import Database
from app.models.enums.role import Role
from app.models.users.user_out import UserOut
from app.security.current_user import CurrentUser
from app.repositories.user_repository import UserRepository


class UserRouter:
    """Wires user endpoints to a UserRepository backed by the given Database."""

    def __init__(self, database: Database, current_user: CurrentUser) -> None:
        self._database = database
        self._current_user = current_user
        self.router = APIRouter(prefix="/api/users", tags=["users"])
        self._register_routes()

    def _get_session(self):
        yield from self._database.session()

    def _register_routes(self) -> None:
        Session = Depends(self._get_session)
        User = Depends(self._current_user.required)

        @self.router.get("", response_model=list[UserOut])
        def list_users(conn: sqlite3.Connection = Session, user: dict = User):
            if user["role"] != Role.ADMIN.value:
                raise HTTPException(status_code=403, detail="Admin only")
            return UserRepository(conn).list()
