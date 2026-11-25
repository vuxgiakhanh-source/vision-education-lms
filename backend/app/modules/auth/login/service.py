import math
import re
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from app.core import clock
from app.core.config import settings
from app.core.logger import logger
from app.core.security import DUMMY_PASSWORD_HASH, create_access_token, validate_password_length, verify_password
from app.database.database import get_session_factory

from .exceptions import (
    UserNotFoundException,
    WrongPasswordException,
    InvalidPhoneNumberException,
    EmptyPasswordException,
    UserLockedException,
    TooManyLoginAttemptsException,
)
from .schemas import LoginRequest, LoginResponse
from .repository import LoginAccount, LoginRepository


# Sai MAX_FAILED_ATTEMPTS lần liên tiếp thì mỗi COOLDOWN chỉ được thử một lần, cho tới khi đăng nhập đúng
# hoặc im lặng quá FAILURE_WINDOW. Giới hạn theo tài khoản, không theo IP vì cả trung tâm dùng chung một IP.
# Đánh đổi: kẻ xấu có thể làm một em phải chờ tối đa COOLDOWN giây, không thể khóa hẳn.
MAX_FAILED_ATTEMPTS = 10
FAILURE_WINDOW = timedelta(minutes=10)
COOLDOWN = timedelta(seconds=60)


def seconds_until_next_attempt(user: LoginAccount, now: datetime) -> int:
    if user.failed_login_count < MAX_FAILED_ATTEMPTS or user.last_failed_login_at is None:
        return 0
    remaining = user.last_failed_login_at + COOLDOWN - now
    return max(0, math.ceil(remaining.total_seconds()))


class LoginService:
    def __init__(self, repository: LoginRepository):
        self.repository = repository

    def record_failed_login(self, user_id: int) -> None:
        self.repository.record_failed_login(user_id, clock.center_local_now(), FAILURE_WINDOW)

    def login(self, request: LoginRequest) -> LoginResponse:
        if not re.match(r"^0\d{9}$", request.phone_number):
            raise InvalidPhoneNumberException()
        if len(request.password) == 0:
            raise EmptyPasswordException()
        validate_password_length(request.password)
        user = self.repository.find_user_by_phone_number(
            request.phone_number
        )
        if user is None:
            # Vẫn chạy bcrypt để thời gian phản hồi bằng trường hợp sai mật khẩu,
            # nếu không đo thời gian là biết số điện thoại nào có tài khoản.
            verify_password(request.password, DUMMY_PASSWORD_HASH)
            logger.warning("Đăng nhập thất bại: Không tìm thấy tài khoản")
            raise UserNotFoundException()
        now = clock.center_local_now()
        retry_after = seconds_until_next_attempt(user, now)
        if retry_after > 0:
            # Chặn TRƯỚC bcrypt: lượt bị chặn không tốn 200 ms CPU.
            logger.warning("Đăng nhập bị tạm chặn: ID {} sai quá nhiều lần", user.id)
            raise TooManyLoginAttemptsException(retry_after)
        if not verify_password(request.password, user.hashed_password):
            # KHÔNG ghi bộ đếm ở đây: lần ghi MySQL (commit) làm mật khẩu sai chậm hơn số lạ khoảng 240 ms,
            # và đo thời gian lại dò ra được số điện thoại nào có tài khoản. Router ghi SAU khi đã trả lời.
            logger.warning("Đăng nhập thất bại: Mật khẩu sai")
            raise WrongPasswordException(user.id)
        if not user.is_active:
            logger.warning(f"Đăng nhập thất bại: Tài khoản ID {user.id} đã bị khóa")
            raise UserLockedException()
        if user.failed_login_count:
            self.repository.clear_failed_logins(user.id)
        logger.info("Đăng nhập thành công: ID {}", user.id)
        return create_login_response(user)


def create_token_payload(user: LoginAccount) -> dict:
    return {
        "id": user.id,
        "role": user.role.value
    }


def create_login_response(user: LoginAccount) -> LoginResponse:
    access_token = create_access_token(create_token_payload(user), timedelta(minutes=settings.access_token_expire_minutes))
    token_type = "bearer"
    return LoginResponse(
        access_token=access_token, token_type=token_type,
        must_change_password=user.must_change_password, role=user.role,
    )



async def get_auth_service(
    session_factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> LoginService:
    return LoginService(LoginRepository(session_factory))
