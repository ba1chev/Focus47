from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.task_record import TaskRecord
from app.models.tasks.task_create import TaskCreate
from app.models.tasks.task_update import TaskUpdate


class TaskRepository:
    """Data-access for tasks. Callers pass a Session per call (stateless)."""

    def list(self, session: Session, start: Optional[str] = None,
        end: Optional[str] = None,
        user_id: Optional[int] = None) -> list[TaskRecord]:
        query = select(TaskRecord)
        if end is not None:
            query = query.where(TaskRecord.start < end)
        if start is not None:
            query = query.where(TaskRecord.end > start)
        if user_id is not None:
            query = query.where(TaskRecord.user_id == user_id)
        query = query.order_by(TaskRecord.start)
        return list(session.execute(query).scalars())

    def get(self, session: Session, task_id: int) -> Optional[TaskRecord]:
        return session.get(TaskRecord, task_id)

    def create(self, session: Session, task: TaskCreate) -> TaskRecord:
        fields = task.model_dump(mode="json", exclude={"repeat_weeks"})
        record = TaskRecord(**fields)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    def update(self, session: Session, task_id: int,
        task: TaskUpdate) -> Optional[TaskRecord]:
        record = session.get(TaskRecord, task_id)
        if record is None:
            return None
        fields = task.model_dump(
            mode="json", exclude_unset=True, exclude={"repeat_weeks"}
        )
        for key, value in fields.items():
            setattr(record, key, value)
        session.commit()
        session.refresh(record)
        return record

    def delete(self, session: Session, task_id: int) -> bool:
        record = session.get(TaskRecord, task_id)
        if record is None:
            return False
        session.delete(record)
        session.commit()
        return True
