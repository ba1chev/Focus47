from pydantic import BaseModel, ConfigDict

from app.models.enums.role import Role


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    account: str
    role: Role
    color: str
