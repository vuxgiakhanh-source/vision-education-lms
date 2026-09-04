from pydantic import BaseModel
from app.core.enums.user_role import UserRole

class MeResponse(BaseModel):
    id: int
    full_name: str
    phone_number: str
    role: UserRole
    must_change_password: bool
    is_active: bool