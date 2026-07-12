import sqlite3
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from db.connection import Database
from app.models.enums.role import Role
from app.models.tasks.task_out import TaskOut
from app.security.current_user import CurrentUser
from app.models.tasks.task_update import TaskUpdate
from app.models.tasks.task_create import TaskCreate
from app.repositories.task_repository import TaskRepository


class TaskRouter:
    """Wires task endpoints to a TaskRepository, scoped to the current user."""

    def __init__(self, database: Database, current_user: CurrentUser) -> None:
        self._database = database
        self._current_user = current_user
        self.router = APIRouter(prefix="/api/tasks", tags=["tasks"])
        self._register_routes()

    def _get_session(self):
        yield from self._database.session()

    def _register_routes(self) -> None:
        Session = Depends(self._get_session)
        User = Depends(self._current_user.required)

        @self.router.get("", response_model=list[TaskOut])
        def list_tasks(
            start: Optional[str] = None,
            end: Optional[str] = None,
            user_id: Optional[int] = None,
            conn: sqlite3.Connection = Session,
            user: dict = User,
        ):
            if user["role"] == Role.ADMIN.value and user_id is not None:
                owner_id = user_id
            else:
                owner_id = user["id"]
            return TaskRepository(conn).list(start=start, end=end, user_id=owner_id)

        @self.router.post("", response_model=TaskOut, status_code=201)
        def create_task(
            task: TaskCreate, conn: sqlite3.Connection = Session, user: dict = User
        ):
            task.user_id = user["id"]
            return TaskRepository(conn).create(task)

        @self.router.get("/{task_id}", response_model=TaskOut)
        def get_task(
            task_id: int, conn: sqlite3.Connection = Session, user: dict = User
        ):
            task = TaskRepository(conn).get(task_id)
            if task is None or task["user_id"] != user["id"]:
                raise HTTPException(status_code=404, detail="Task not found")
            return task

        @self.router.patch("/{task_id}", response_model=TaskOut)
        def update_task(
            task_id: int, task: TaskUpdate,
            conn: sqlite3.Connection = Session, user: dict = User
        ):
            repo = TaskRepository(conn)
            existing = repo.get(task_id)
            if existing is None or existing["user_id"] != user["id"]:
                raise HTTPException(status_code=404, detail="Task not found")
            return repo.update(task_id, task)

        @self.router.delete("/{task_id}", status_code=204)
        def delete_task(
            task_id: int, conn: sqlite3.Connection = Session, user: dict = User
        ):
            repo = TaskRepository(conn)
            existing = repo.get(task_id)
            if existing is None or existing["user_id"] != user["id"]:
                raise HTTPException(status_code=404, detail="Task not found")
            repo.delete(task_id)
