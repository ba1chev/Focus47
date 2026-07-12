from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from db.base import utcnow


class DateTimeMixin:
    """Reusable created_at / updated_at timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
