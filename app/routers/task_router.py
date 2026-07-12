from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException

from db.engine import Database
from app.models.enums.role import Role
from db.models.user_record import UserRecord
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
        self._repo = TaskRepository()
        self.router = APIRouter(prefix="/api/tasks", tags=["tasks"])
        self._register_routes()

    def _get_session(self):
        with self._database.session() as session:
            yield session

    def _spawn_weekly_copies(self, session: Session, template: TaskCreate, weeks: int) -> None:
        for k in range(1, weeks + 1):
            copy = template.model_copy(update={
                "start": self._shift_weeks(template.start, k),
                "end": self._shift_weeks(template.end, k),
                "repeat_weeks": 0
            })
            self._repo.create(session, copy)

    @staticmethod
    def _shift_weeks(iso: str, weeks: int) -> str:
        return (datetime.fromisoformat(iso) + timedelta(weeks=weeks)).isoformat()

    def _register_routes(self) -> None:
        SessionDep = Depends(self._get_session)
        User = Depends(self._current_user.required)

        @self.router.get("", response_model=list[TaskOut])
        def list_tasks(
            start: Optional[str] = None,
            end: Optional[str] = None,
            user_id: Optional[int] = None,
            session: Session = SessionDep,
            user: UserRecord = User
        ):
            if user.role == Role.ADMIN.value and user_id is not None:
                owner_id = user_id
            else:
                owner_id = user.id
            return self._repo.list(session, start=start, end=end, user_id=owner_id)

        @self.router.post("", response_model=TaskOut, status_code=201)
        def create_task(
            task: TaskCreate, session: Session = SessionDep, user: UserRecord = User
        ):
            task.user_id = user.id
            record = self._repo.create(session, task)
            if task.repeat_weeks > 0:
                self._spawn_weekly_copies(session, task, task.repeat_weeks)
            return record

        @self.router.get("/{task_id}", response_model=TaskOut)
        def get_task(
            task_id: int, session: Session = SessionDep, user: UserRecord = User
        ):
            task = self._repo.get(session, task_id)
            if task is None or task.user_id != user.id:
                raise HTTPException(status_code=404, detail="Task not found")
            return task

        @self.router.patch("/{task_id}", response_model=TaskOut)
        def update_task(
            task_id: int, task: TaskUpdate,
            session: Session = SessionDep, user: UserRecord = User
        ):
            existing = self._repo.get(session, task_id)
            if existing is None or existing.user_id != user.id:
                raise HTTPException(status_code=404, detail="Task not found")
            record = self._repo.update(session, task_id, task)
            if task.repeat_weeks > 0:
                template = TaskCreate.model_validate(record)
                self._spawn_weekly_copies(session, template, task.repeat_weeks)
            return record

        @self.router.delete("/{task_id}", status_code=204)
        def delete_task(
            task_id: int, session: Session = SessionDep, user: UserRecord = User
        ):
            existing = self._repo.get(session, task_id)
            if existing is None or existing.user_id != user.id:
                raise HTTPException(status_code=404, detail="Task not found")
            self._repo.delete(session, task_id)
