from fastapi import FastAPI
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from db.connection import Database
from db.schema import SchemaInitializer
from app.routers.task_router import TaskRouter
from app.routers.user_router import UserRouter
from app.config import (
    APP_TITLE, DEFAULT_COLOR, DEFAULT_USER_NAME,
    STATIC_DIR, TEMPLATES_DIR
)


class Application:
    """Composition root: builds the Database, routers and FastAPI app."""

    def __init__(self, database: Database | None = None) -> None:
        self._database = database or Database()
        self._schema = SchemaInitializer(
            self._database,
            default_user_name=DEFAULT_USER_NAME,
            default_user_color=DEFAULT_COLOR,
        )
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            self._schema.initialize()
            yield

        app = FastAPI(title=APP_TITLE, lifespan=lifespan)
        app.include_router(TaskRouter(self._database).router)
        app.include_router(UserRouter(self._database).router)

        @app.get("/")
        def index():
            return FileResponse(TEMPLATES_DIR / "index.html")

        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
        return app


app = Application().app
