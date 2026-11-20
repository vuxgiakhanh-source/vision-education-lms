import re
from datetime import timedelta
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logger import logger
from app.core.security import create_access_token, validate_password_length, verify_password
from app.database.database import get_session_factory

from .exceptions import (
    UserNotFoundException,
    WrongPasswordException,
    InvalidPhoneNumberException,
    EmptyPasswordException,
    UserLockedException
)
from .schemas import LoginRequest, LoginResponse
from .repository import LoginAccount, LoginRepository


class LoginService:
    def __init__(self, repository: LoginRepository):
        self.repository = repository

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
            logger.warning("Đăng nhập thất bại: Không tìm thấy tài khoản")
            raise UserNotFoundException()
        if not verify_password(request.password, user.hashed_password):
            logger.warning("Đăng nhập thất bại: Mật khẩu sai")
            raise WrongPasswordException()
        if not user.is_active:
            logger.warning(f"Đăng nhập thất bại: Tài khoản ID {user.id} đã bị khóa")
            raise UserLockedException()
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
    return LoginResponse(access_token=access_token, token_type=token_type, must_change_password=user.must_change_password)



async def get_auth_service(
    session_factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> LoginService:
    return LoginService(LoginRepository(session_factory))
