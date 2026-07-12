from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from db.engine import Database
from app.models.enums.role import Role
from db.models.user_record import UserRecord
from app.models.users.user_out import UserOut
from app.security.current_user import CurrentUser
from app.repositories.user_repository import UserRepository


class UserRouter:
    """Wires user endpoints to a UserRepository backed by the given Database."""

    def __init__(self, database: Database, current_user: CurrentUser) -> None:
        self._database = database
        self._current_user = current_user
        self._repo = UserRepository()
        self.router = APIRouter(prefix="/api/users", tags=["users"])
        self._register_routes()

    def _get_session(self):
        with self._database.session() as session:
            yield session

    def _register_routes(self) -> None:
        SessionDep = Depends(self._get_session)
        User = Depends(self._current_user.required)

        @self.router.get("", response_model=list[UserOut])
        def list_users(session: Session = SessionDep, user: UserRecord = User):
            if user.role != Role.ADMIN.value:
                raise HTTPException(status_code=403, detail="Admin only")
            return self._repo.list(session)
