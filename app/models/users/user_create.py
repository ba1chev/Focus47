from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    color: str = "#6264a7"