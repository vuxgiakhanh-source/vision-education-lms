from fastapi import APIRouter, Depends, HTTPException
from .schemas import LoginRequest, LoginResponse
from .service import AuthService, get_auth_service, create_token_payload, create_login_response
from .exceptions import UserNotFoundException, WrongPasswordException
from app.core.security import create_access_token

auth_router = APIRouter()

@auth_router.post("/login")
def login(login_request: LoginRequest, 
          auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return auth_service.login(login_request)
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

