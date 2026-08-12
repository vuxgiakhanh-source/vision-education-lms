from fastapi import APIRouter, Depends, HTTPException
from .schemas import LoginRequest
from .service import AuthService, get_auth_service
from .exceptions import UserNotFoundException, WrongPasswordException

auth_router = APIRouter()

@auth_router.post("/login")
def login(login_request: LoginRequest, 
          auth_service: AuthService = Depends(get_auth_service)
):
    try:
        auth_service.login(login_request)
    except UserNotFoundException:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    except WrongPasswordException:
        raise HTTPException(
            status_code=401,
            detail="Wrong password"
        )
    return {
        "message": "Login success"
    }


