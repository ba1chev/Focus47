from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums.role import Role
from db.models.user_record import UserRecord


class UserRepository:
    """Data-access for users. Callers pass a Session per call (stateless)."""

    def list(self, session: Session) -> list[UserRecord]:
        return list(
            session.execute(
                select(UserRecord).order_by(UserRecord.id)
            ).scalars()
        )

    def get(self, session: Session, user_id: int) -> Optional[UserRecord]:
        return session.get(UserRecord, user_id)

    def get_by_account(self, session: Session, account: str) -> Optional[UserRecord]:
        return session.execute(
            select(UserRecord).where(UserRecord.account == account)
        ).scalar_one_or_none()

    def create(self, session: Session, name: str, account: str,
        password_hash: str, role: Role = Role.REGULAR,
        color: str = "#6264a7") -> UserRecord:
        user = UserRecord(
            name=name, account=account, password_hash=password_hash,
            role=role.value, color=color
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
