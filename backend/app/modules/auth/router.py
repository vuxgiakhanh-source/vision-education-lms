from fastapi import APIRouter
from .schemas import LoginRequest

auth_router = APIRouter()

@auth_router.post("/login")
def login(login_request: LoginRequest):

    print(login_request.phone_number)

    print(login_request.password)

    return {
        "message": "Login success"
    }


