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
from app.models.user import User
from app.core.security import create_access_token
from app.modules.auth.schemas import LoginResponse
from datetime import timedelta
from app.core.config import settings


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
        return create_login_response(user)

def create_token_payload(user: User) -> dict:
    return {
        "id": user.id,
        "role": user.role
    }
def create_login_response(user: User) -> LoginResponse:
    access_token = create_access_token(create_token_payload(user), timedelta(minutes=settings.access_token_expire_minutes))
    token_type = "bearer"
    return LoginResponse(access_token=access_token, token_type=token_type)

#Để ở cuối
def get_auth_service(db: Session = Depends(get_db)):
    repository = AuthRepository(db)
    return AuthService(repository)


    