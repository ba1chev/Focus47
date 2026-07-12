from typing import Optional
from fastapi import Request, HTTPException

from db.engine import Database
from app.constants import COOKIE_NAME
from db.models.user_record import UserRecord
from app.security.token_service import TokenService
from app.repositories.user_repository import UserRepository


class CurrentUser:
    """Resolves the authenticated user from the JWT access-token cookie."""

    def __init__(self, database: Database, token_service: TokenService) -> None:
        self._database = database
        self._token_service = token_service

    def _resolve(self, request: Request) -> Optional[UserRecord]:
        token = request.cookies.get(COOKIE_NAME)
        if not token:
            return None
        payload = self._token_service.decode(token)
        if not payload:
            return None
        with self._database.session() as session:
            return UserRepository().get(session, int(payload["sub"]))

    def optional(self, request: Request) -> Optional[UserRecord]:
        return self._resolve(request)

    def required(self, request: Request) -> UserRecord:
        user = self._resolve(request)
        if user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return user
