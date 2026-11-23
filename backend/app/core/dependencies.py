from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from app.core.enums.user_role import UserRole
from app.core.security import decode_access_token
from app.database.database import get_session_factory
from app.models.user import User

security = HTTPBearer()

ACCOUNT_LOCKED_DETAIL = {
    "code": "ACCOUNT_LOCKED",
    "message": "Tài khoản của bạn đã bị khóa",
}

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)    
) -> int:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token thiếu user id"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn"
        )


def _get_lms_role(user_id: int, session_factory: sessionmaker[Session]) -> UserRole:
    with session_factory() as db:
        account = db.execute(
            select(User.is_active, User.must_change_password, User.role).where(User.id == user_id)
        ).one_or_none()
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại trong hệ thống",
        )
    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ACCOUNT_LOCKED_DETAIL,
        )
    if account.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vui lòng đổi mật khẩu trước khi tiếp tục",
        )
    return account.role


def require_student_access(
    user_id: Annotated[int, Depends(get_current_user_id)],
    session_factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> int:
    if _get_lms_role(user_id, session_factory) != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh mới có quyền truy cập",
        )
    return user_id


def require_teacher_access(
    user_id: Annotated[int, Depends(get_current_user_id)],
    session_factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> int:
    if _get_lms_role(user_id, session_factory) != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ giáo viên mới có quyền truy cập",
        )
    return user_id
