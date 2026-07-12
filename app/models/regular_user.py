from app.models.user import User
from app.models.enums.role import Role


class RegularUser(User):
    role: Role = Role.REGULAR
