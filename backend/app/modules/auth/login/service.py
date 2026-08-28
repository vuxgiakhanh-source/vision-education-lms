from .exceptions import (
    UserNotFoundException,
    WrongPasswordException,
    InvalidPhoneNumberException,
    EmptyPasswordException
)
from .schemas import LoginRequest, LoginResponse
from .repository import LoginRepository
from app.core.security import verify_password
from app.database.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import create_access_token
from datetime import timedelta
from app.core.config import settings
from app.core.logger import logger


class LoginService:
    def __init__(self, repository: LoginRepository):
        self.repository = repository

    def login(self, request: LoginRequest):
        if len(request.phone_number) != 10:
            raise InvalidPhoneNumberException()
        if len(request.password) == 0:
            raise EmptyPasswordException()
        user = self.repository.find_user_by_phone_number(
            request.phone_number
        )
        if user is None:
            logger.warning(f"Đăng nhập thất bại: Không tìm thấy tài khoản SDT {request.phone_number}")
            raise UserNotFoundException()
        if not verify_password(request.password, user.hashed_password):
            logger.warning("Đăng nhập thất bại: Mật khẩu sai con ơi")
            raise WrongPasswordException()
        logger.info(f"Đăng nhập thành công: ID {request.phone_number}, Sdt {request.phone_number}")
        return create_login_response(user)
    def get_user_by_id(self, user_id: int):
        user = self.repository.find_user_by_id(user_id)
        if not user:
            logger.warning(f"Tìm kiếm thất bại: Không tìm thấy tài khoản ID {user_id}")
            raise UserNotFoundException()
        return self.repository.find_user_by_id(user_id)

def create_token_payload(user: User) -> dict:
    return {
        "id": user.id,
        "role": user.role.value
    }
def create_login_response(user: User) -> LoginResponse:
    access_token = create_access_token(create_token_payload(user), timedelta(minutes=settings.access_token_expire_minutes))
    token_type = "bearer"
    return LoginResponse(access_token=access_token, token_type=token_type, must_change_password=user.must_change_password)

#Để ở cuối
def get_auth_service(db: Session = Depends(get_db)):
    repository = LoginRepository(db)
    return LoginService(repository)




    