import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Response

from db.connection import Database
from app.constants import COOKIE_NAME
from app.models.users.user_out import UserOut
from app.security.current_user import CurrentUser
from app.security.token_service import TokenService
from app.models.auth.login_request import LoginRequest
from app.security.password_hasher import PasswordHasher
from app.repositories.user_repository import UserRepository
from app.models.auth.register_request import RegisterRequest


class AuthRouter:
    """Wires registration, login, logout and current-user endpoints."""

    def __init__(self, database: Database, password_hasher: PasswordHasher,
        token_service: TokenService, current_user: CurrentUser) -> None:
        self._database = database
        self._hasher = password_hasher
        self._tokens = token_service
        self._current_user = current_user
        self.router = APIRouter(prefix="/api/auth", tags=["auth"])
        self._register_routes()

    def _get_session(self):
        yield from self._database.session()

    def _set_cookie(self, response: Response, user: dict) -> None:
        token = self._tokens.create(user["id"], user["role"])
        response.set_cookie(
            key=COOKIE_NAME, value=token,
            httponly=True, samesite="lax"
        )

    def _register_routes(self) -> None:
        Session = Depends(self._get_session)

        @self.router.post("/register", response_model=UserOut, status_code=201)
        def register(payload: RegisterRequest, response: Response,
            conn: sqlite3.Connection = Session):
            repo = UserRepository(conn)
            if repo.get_by_account(payload.account):
                raise HTTPException(status_code=409, detail="Account already exists")
            user = repo.create(
                name=payload.name,
                account=payload.account,
                password_hash=self._hasher.hash(payload.password)
            )
            self._set_cookie(response, user)
            return user

        @self.router.post("/login", response_model=UserOut)
        def login(payload: LoginRequest, response: Response,
            conn: sqlite3.Connection = Session):
            user = UserRepository(conn).get_by_account(payload.account)
            if not user or not self._hasher.verify(
                payload.password, user["password_hash"]
            ):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            self._set_cookie(response, user)
            return user

        @self.router.post("/logout", status_code=204)
        def logout(response: Response):
            response.delete_cookie(COOKIE_NAME)

        @self.router.get("/me", response_model=UserOut)
        def me(user: dict = Depends(self._current_user.required)):
            return user
