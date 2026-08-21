from fastapi import APIRouter, Depends, HTTPException
from .schemas import LoginRequest, LoginResponse
from .service import AuthService, get_auth_service, create_token_payload, create_login_response
from .exceptions import UserNotFoundException, WrongPasswordException, InvalidPhoneNumberException, EmptyPasswordException
from app.core.security import create_access_token
from app.core.logger import logger
auth_router = APIRouter()

@auth_router.post("/login")
def login(login_request: LoginRequest, 
          auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return auth_service.login(login_request)
    except UserNotFoundException:
        raise HTTPException(
            status_code=401,
            detail="Mật khẩu hoặc số điện thoại không đúng"
        )
    except WrongPasswordException:
        raise HTTPException(
            status_code=401,
            detail="Mật khẩu hoặc số điện thoại không đúng"
        )
    except InvalidPhoneNumberException:
        logger.warning(f"Sdt: {login_request.phone_number} không hợp lệ")
        raise HTTPException(
            status_code=400,
            detail="Số điện thoại phải có đúng 10 chữ số"
        )
    except EmptyPasswordException:
        logger.warning(f"Đăng nhập thất bại: Mật khẩu không được để trống :)")
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu không được để trống"
        )

