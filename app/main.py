from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from db.engine import Database
from db.schema import SchemaInitializer
from app.routers.task_router import TaskRouter
from app.routers.user_router import UserRouter
from app.routers.auth_router import AuthRouter
from app.security.current_user import CurrentUser
from app.security.token_service import TokenService
from app.security.password_hasher import PasswordHasher
from app.config import (
    APP_TITLE, DEFAULT_COLOR,
    ADMIN_ACCOUNT, ADMIN_PASSWORD, JWT_SECRET, JWT_TTL_HOURS,
    STATIC_DIR, TEMPLATES_DIR,
)


class Application:
    """Composition root: builds the Database, security, routers and FastAPI app."""

    def __init__(self, database: Database | None = None) -> None:
        self._database = database or Database()
        self._hasher = PasswordHasher()
        self._tokens = TokenService(JWT_SECRET, ttl_hours=JWT_TTL_HOURS)
        self._current_user = CurrentUser(self._database, self._tokens)
        self._schema = SchemaInitializer(
            self._database,
            admin_account=ADMIN_ACCOUNT,
            admin_password_hash=self._hasher.hash(ADMIN_PASSWORD),
            admin_color=DEFAULT_COLOR
        )
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            self._schema.initialize()
            yield

        app = FastAPI(title=APP_TITLE, lifespan=lifespan)
        app.include_router(
            AuthRouter(
                self._database, self._hasher, self._tokens, self._current_user
            ).router
        )
        app.include_router(TaskRouter(self._database, self._current_user).router)
        app.include_router(UserRouter(self._database, self._current_user).router)

        @app.get("/")
        def index(request: Request):
            if self._current_user.optional(request) is None:
                return RedirectResponse("/login", status_code=303)
            return FileResponse(TEMPLATES_DIR / "index.html")

        @app.get("/login")
        def login_page():
            return FileResponse(TEMPLATES_DIR / "login.html")

        @app.get("/register")
        def register_page():
            return FileResponse(TEMPLATES_DIR / "register.html")

        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
        return app


app = Application().app
