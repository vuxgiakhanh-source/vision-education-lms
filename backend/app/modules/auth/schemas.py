from pydantic import BaseModel
from 

class LoginRequest(BaseModel):
    phone_number: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"