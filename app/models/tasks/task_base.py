from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.enums.status import Status
from app.models.enums.priority import Priority


class TaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: str = ""
    start: str
    end: str
    status: Status = Status.TODO
    priority: Priority = Priority.MEDIUM
    category: str = ""
    user_id: Optional[int] = None