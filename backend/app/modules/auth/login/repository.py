from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.enums.user_role import UserRole
from app.models.user import User


@dataclass(frozen=True)
class LoginAccount:
    id: int
    role: UserRole
    hashed_password: str = field(repr=False)
    is_active: bool
    must_change_password: bool


class LoginRepository:
    def __init__(self, session_factory: sessionmaker[Session]):
        self.session_factory = session_factory

    def find_user_by_phone_number(self, phone_number: str) -> LoginAccount | None:
        statement = select(
            User.id, User.role, User.hashed_password, User.is_active, User.must_change_password
        ).where(User.phone_number == phone_number)

        with self.session_factory() as db:
            account = db.execute(statement).mappings().one_or_none()
            return LoginAccount(**account) if account is not None else None
