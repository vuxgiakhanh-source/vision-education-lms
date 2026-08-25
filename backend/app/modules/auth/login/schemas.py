from pydantic import BaseModel
from app.core.enums.user_role import UserRole

class LoginRequest(BaseModel):
    phone_number: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    full_name: str
    phone_number: str
    role: UserRole
    must_change_password: bool
