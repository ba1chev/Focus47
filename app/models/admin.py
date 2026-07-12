from app.models.user import User
from app.models.enums.role import Role


class Admin(User):
    role: Role = Role.ADMIN
