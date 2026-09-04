from fastapi import APIRouter, Depends, HTTPException
from .service import MeService, get_me_service
from .exceptions import UserLockedException, UserNotFoundException
from app.core.dependencies import get_current_user_id

me_router = APIRouter()

@me_router.get("/me")
def get_me(user_id: int = Depends(get_current_user_id),
            me_service: MeService = Depends(get_me_service)
):
    try:
        return me_service.get_me_response(user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=401,
            detail="Tài khoản không tồn tại trong hệ thống"
        )
    except UserLockedException:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản của bạn đã bị khóa"
        )