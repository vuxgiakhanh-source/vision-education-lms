from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy import case, or_, select, update
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
    failed_login_count: int
    last_failed_login_at: datetime | None


class LoginRepository:
    def __init__(self, session_factory: sessionmaker[Session]):
        self.session_factory = session_factory

    def find_user_by_phone_number(self, phone_number: str) -> LoginAccount | None:
        statement = select(
            User.id, User.role, User.hashed_password, User.is_active, User.must_change_password,
            User.failed_login_count, User.last_failed_login_at,
        ).where(User.phone_number == phone_number)

        with self.session_factory() as db:
            account = db.execute(statement).mappings().one_or_none()
            return LoginAccount(**account) if account is not None else None

    def record_failed_login(self, user_id: int, now: datetime, window: timedelta) -> None:
        """Tăng bộ đếm bằng MỘT câu UPDATE nguyên tử, không đọc rồi ghi lại (nhiều worker cùng đăng nhập sai).

        Quá `window` kể từ lần sai trước thì đếm lại từ 1. ordered_values giữ đúng thứ tự gán vì MySQL
        gán từ trái sang phải: bộ đếm phải đọc last_failed_login_at CŨ trước khi nó bị ghi đè.
        updated_at giữ nguyên, đăng nhập sai không phải là sửa hồ sơ.
        """
        starts_over = or_(User.last_failed_login_at.is_(None), User.last_failed_login_at < now - window)
        with self.session_factory.begin() as db:
            db.execute(
                update(User)
                .where(User.id == user_id)
                .ordered_values(
                    (User.failed_login_count, case((starts_over, 1), else_=User.failed_login_count + 1)),
                    (User.last_failed_login_at, now),
                    (User.updated_at, User.updated_at),
                )
            )

    def clear_failed_logins(self, user_id: int) -> None:
        with self.session_factory.begin() as db:
            db.execute(
                update(User)
                .where(User.id == user_id)
                .ordered_values(
                    (User.failed_login_count, 0),
                    (User.last_failed_login_at, None),
                    (User.updated_at, User.updated_at),
                )
            )
