from types import SimpleNamespace

from app.models.enums.status import Status
from app.models.tasks.task_out import TaskOut
from app.models.enums.priority import Priority
from app.models.tasks.task_create import TaskCreate
from app.models.tasks.task_update import TaskUpdate


def test_task_create_defaults():
    task = TaskCreate(title="X", start="2026-07-13T09:00:00", end="2026-07-13T10:00:00")
    assert task.repeat_weeks == 0
    assert task.status == Status.TODO
    assert task.priority == Priority.MEDIUM
    assert task.description == ""


def test_task_create_accepts_repeat_weeks():
    task = TaskCreate(
        title="X", start="2026-07-13T09:00:00", end="2026-07-13T10:00:00",
        repeat_weeks=4
    )
    assert task.repeat_weeks == 4


def test_task_update_repeat_weeks_default():
    assert TaskUpdate().repeat_weeks == 0


def test_task_out_reads_from_orm_attributes():
    record = SimpleNamespace(
        id=42, title="Standup", description="", start="2026-07-13T09:00:00",
        end="2026-07-13T09:30:00", status="todo", priority="medium",
        category="", user_id=1
    )
    out = TaskOut.model_validate(record)
    assert out.id == 42
    assert out.title == "Standup"
    assert out.user_id == 1


def test_task_update_partial_leaves_unset_fields():
    update = TaskUpdate(title="New title")
    dumped = update.model_dump(exclude_unset=True)
    assert dumped == {"title": "New title"}
