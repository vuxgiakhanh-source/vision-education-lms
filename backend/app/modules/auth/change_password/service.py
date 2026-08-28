from .exceptions import (
    EmptyNewPasswordException, 
    PasswordUnchangedException,
    UserNotFoundException
)
from .schemas import ChangePasswordRequest, ChangePasswordResponse
from .repository import ChangePasswordRepository
from app.core.security import hash_password, verify_password
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.database import get_db


class ChangePasswordService:
    def __init__(self, repository: ChangePasswordRepository):
        self.repository = repository
    def change_password(self, request: ChangePasswordRequest, user_id: int):
        if not request.new_password:
            raise EmptyNewPasswordException()
        user = self.repository.find_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        if verify_password(request.new_password, user.hashed_password):
            raise PasswordUnchangedException()
        new_hashed_password = hash_password(request.new_password)
        self.repository.change_password(user, new_hashed_password)
        return create_change_password_response()
def create_change_password_response() -> ChangePasswordResponse:
    return ChangePasswordResponse(message="Đổi mật khẩu thành công")
#Để ở cuối
def get_change_password_service(db: Session = Depends(get_db)):
    repository = ChangePasswordRepository(db)
    return ChangePasswordService(repository)
