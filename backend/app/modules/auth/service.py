from .exceptions import (
    UserNotFoundException,
    WrongPasswordException
)
from .schemas import LoginRequest
from .repository import AuthRepository
from backend.app.core.security import verify_password

class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def login(self, request: LoginRequest):
        user = self.repository.find_by_phone_number(
            request.phone_number
        )
        if user is None:
            raise UserNotFoundException()
        if not verify_password(request.password, user.hashed_password):
            raise WrongPasswordException()
  

    