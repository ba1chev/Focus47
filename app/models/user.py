from pydantic import BaseModel

from app.config import DEFAULT_COLOR
from app.models.enums.role import Role


class User(BaseModel):
    id: int
    name: str
    account: str
    role: Role
    color: str = DEFAULT_COLOR
