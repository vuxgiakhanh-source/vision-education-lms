from typing import Annotated

from anyio import CapacityLimiter, to_thread
from anyio.lowlevel import RunVar
from fastapi import APIRouter, Depends, HTTPException

from app.core.logger import logger
from app.core.security import InvalidPasswordError

from .exceptions import (
    EmptyPasswordException,
    InvalidPhoneNumberException,
    UserLockedException,
    UserNotFoundException,
    WrongPasswordException,
)
from .schemas import LoginRequest
from .service import LoginService, get_auth_service


login_router = APIRouter()
MAX_CONCURRENT_LOGINS = 4
_login_limiter = RunVar[CapacityLimiter]("login_limiter")


def get_login_limiter() -> CapacityLimiter:
    limiter = _login_limiter.get(None)
    if limiter is None:
        limiter = CapacityLimiter(MAX_CONCURRENT_LOGINS)
        _login_limiter.set(limiter)
    return limiter


@login_router.post("/login")
async def login(
    login_request: LoginRequest,
    auth_service: Annotated[LoginService, Depends(get_auth_service)],
):
    try:
        # Keep password verification from consuming the shared synchronous capacity.
        return await to_thread.run_sync(auth_service.login, login_request, limiter=get_login_limiter())
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
        logger.warning("Đăng nhập thất bại: Số điện thoại không hợp lệ")
        raise HTTPException(
            status_code=400,
            detail="Số điện thoại phải có đúng 10 chữ số"
        )
    except EmptyPasswordException:
        logger.warning(f"Đăng nhập thất bại: Mật khẩu không được để trống")
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu không được để trống"
        )
    except InvalidPasswordError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UserLockedException:
        logger.warning(f"Đăng nhập thất bại: Tài khoản đã bị khóa")
        raise HTTPException(
            status_code=403,
            detail="Tài khoản của bạn đã bị khóa"
        )

