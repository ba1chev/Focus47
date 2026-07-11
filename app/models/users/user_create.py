from pydantic import BaseModel

from app.config import DEFAULT_COLOR


class UserCreate(BaseModel):
    name: str
    color: str = DEFAULT_COLOR