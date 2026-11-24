from datetime import datetime, timezone
from app.core.enums.user_role import UserRole
from app.core.base import Base
from sqlalchemy import Integer, Column, String, Boolean, Enum, DateTime, UniqueConstraint


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("phone_number", name="uq_users_phone_number"),)
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    must_change_password = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    # Giới hạn đăng nhập sai theo tài khoản (không theo IP: 500 em dùng chung một IP Wi-Fi của trung tâm).
    failed_login_count = Column(Integer, nullable=False, default=0, server_default="0")
    last_failed_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

