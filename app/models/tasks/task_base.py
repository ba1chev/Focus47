from typing import Optional
from pydantic import BaseModel

from app.config import DEFAULT_COLOR
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
    color: str = DEFAULT_COLOR
    user_id: Optional[int] = None