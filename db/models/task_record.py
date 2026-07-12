from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class TaskRecord(Base):
    """A calendar task owned by a user, spanning a start/end datetime."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str] = mapped_column(default="", server_default="")
    start: Mapped[str]
    end: Mapped[str]
    status: Mapped[str] = mapped_column(
        default="todo", server_default="todo", index=True
    )
    priority: Mapped[str] = mapped_column(default="medium", server_default="medium")
    category: Mapped[str] = mapped_column(default="", server_default="")
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
