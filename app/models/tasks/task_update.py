from typing import Optional
from pydantic import BaseModel

from app.models.enums.status import Status
from app.models.enums.priority import Priority


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    category: Optional[str] = None
    user_id: Optional[int] = None