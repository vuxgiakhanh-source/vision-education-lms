from typing import Annotated

from anyio import CapacityLimiter, to_thread
from anyio.lowlevel import RunVar
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask

from app.core.logger import logger
from app.core.security import InvalidPasswordError

from .exceptions import (
    EmptyPasswordException,
    InvalidPhoneNumberException,
    TooManyLoginAttemptsException,
    UserLockedException,
    UserNotFoundException,
    WrongPasswordException,
)
from .schemas import LoginRequest, LoginResponse
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


@login_router.post("/login", response_model=LoginResponse)
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
    except WrongPasswordException as exc:
        # Trả lời trước, ghi bộ đếm sau. Phải trả JSONResponse có background: BackgroundTasks của FastAPI
        # bị bỏ khi endpoint ném HTTPException.
        return JSONResponse(
            status_code=401,
            content={"detail": "Mật khẩu hoặc số điện thoại không đúng"},
            background=BackgroundTask(auth_service.record_failed_login, exc.user_id),
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
    except TooManyLoginAttemptsException as exc:
        raise HTTPException(
            status_code=429,
            detail=f"Đăng nhập sai quá nhiều lần. Vui lòng thử lại sau {exc.retry_after_seconds} giây.",
            headers={"Retry-After": str(exc.retry_after_seconds)},
        )
    except UserLockedException:
        logger.warning(f"Đăng nhập thất bại: Tài khoản đã bị khóa")
        raise HTTPException(
            status_code=403,
            detail="Tài khoản của bạn đã bị khóa"
        )

