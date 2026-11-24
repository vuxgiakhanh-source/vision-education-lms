from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_teacher_access
from app.database.database import DbSession

from .move_session.router import move_session_router
from .repository import TeachingSessionRepository
from .schemas import TeachingSessionResponse
from .service import TeachingSessionService
from .swap_sessions.router import swap_sessions_router


teaching_session_router = APIRouter(
    prefix="/teacher/sessions",
    dependencies=[Depends(require_teacher_access)],
)
teaching_session_router.include_router(move_session_router)
teaching_session_router.include_router(swap_sessions_router)


def get_teaching_session_service(db: DbSession) -> TeachingSessionService:
    return TeachingSessionService(TeachingSessionRepository(db))


@teaching_session_router.get("/{session_id}")
def get_session(
    session_id: Annotated[int, Path(gt=0)],
    service: Annotated[TeachingSessionService, Depends(get_teaching_session_service)],
) -> TeachingSessionResponse:
    session = service.get_session_detail(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy buổi dạy")
    return session
