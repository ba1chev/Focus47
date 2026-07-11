from typing import Optional
from pydantic import BaseModel

from app.models.enums.status import Status
from app.models.enums.priority import Priority


class TaskBase(BaseModel):
    title: str
    description: str = ""
    start: str
    end: str
    status: Status = Status.TODO
    priority: Priority = Priority.MEDIUM
    category: str = ""
    user_id: Optional[int] = None