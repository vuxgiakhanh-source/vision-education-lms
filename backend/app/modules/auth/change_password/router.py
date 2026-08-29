from .schemas import ChangePasswordRequest
from fastapi import APIRouter, Depends, HTTPException, status
from .service import ChangePasswordService, get_change_password_service
from app.core.dependencies import get_current_user_id
from .exceptions import (
    EmptyNewPasswordException,
    PasswordUnchangedException,
    UserNotFoundException
)

change_password_router = APIRouter()

@change_password_router.put("/change-password")
def change_password(
    change_password_request: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    change_password_service: ChangePasswordService = Depends(get_change_password_service)
):
    try:
        return change_password_service.change_password(change_password_request, user_id)                 
    except EmptyNewPasswordException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới không được để trống :)"
        )
    except PasswordUnchangedException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới trùng với mật khẩu cũ"
        )
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tài khoản không tồn tại hoặc đã bị vô hiệu hóa"
        )

