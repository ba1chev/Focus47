from pydantic import BaseModel


class RegisterRequest(BaseModel):
    name: str
    account: str
    password: str
