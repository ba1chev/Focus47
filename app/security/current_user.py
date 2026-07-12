import sqlite3
from typing import Optional
from fastapi import Request, HTTPException

from db.connection import Database
from app.security.token_service import TokenService
from app.repositories.user_repository import UserRepository

COOKIE_NAME = "access_token"


class CurrentUser:
    """Resolves the authenticated user from the JWT access-token cookie."""

    def __init__(self, database: Database, token_service: TokenService) -> None:
        self._database = database
        self._token_service = token_service

    def _resolve(self, request: Request) -> Optional[dict]:
        token = request.cookies.get(COOKIE_NAME)
        if not token:
            return None
        payload = self._token_service.decode(token)
        if not payload:
            return None
        conn = self._database.connect()
        try:
            return UserRepository(conn).get(int(payload["sub"]))
        finally:
            conn.close()

    def optional(self, request: Request) -> Optional[dict]:
        return self._resolve(request)

    def required(self, request: Request) -> dict:
        user = self._resolve(request)
        if user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return user
