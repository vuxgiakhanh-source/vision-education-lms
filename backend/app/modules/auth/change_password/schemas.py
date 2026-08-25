from pydantic import BaseModel
class ChangePasswordRequest(BaseModel):
    old_password: str | None = None
    new_password: str
class ChangePasswordResponse(BaseModel):
    message: str