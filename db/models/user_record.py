from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class UserRecord(Base):
    """A Focus47 account: admin or regular, identified by a unique account name."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    account: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    role: Mapped[str] = mapped_column(default="regular", server_default="regular")
    color: Mapped[str] = mapped_column(default="#6264a7", server_default="#6264a7")
