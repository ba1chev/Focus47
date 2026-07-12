from app.models.tasks.task_base import TaskBase


class TaskCreate(TaskBase):
    repeat_weeks: int = 0
