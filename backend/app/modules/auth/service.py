from .exceptions import (
    UserNotFoundException,
    WrongPasswordException
)
from .schemas import LoginRequest
from .repository import AuthRepository
from app.core.security import verify_password
from app.database.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def login(self, request: LoginRequest):
        user = self.repository.find_user_by_phone_number(
            request.phone_number
        )
        if user is None:
            raise UserNotFoundException()
        if not verify_password(request.password, user.hashed_password):
            raise WrongPasswordException()
        return user
#Để ở cuối
def get_auth_service(db: Session = Depends(get_db)):
    repository = AuthRepository(db)
    return AuthService(repository)

    