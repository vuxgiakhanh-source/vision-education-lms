from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_student_access
from app.database.database import DbSession

from ..exceptions import StudentGradeNotFoundException
from ..repository import ScheduleRepository
from .schemas import UpcomingSessionResponse
from .service import StudentUpcomingSessionService


student_upcoming_router = APIRouter()


def get_student_upcoming_service(db: DbSession) -> StudentUpcomingSessionService:
    return StudentUpcomingSessionService(ScheduleRepository(db))


@student_upcoming_router.get("/schedule/upcoming")
def get_upcoming_session(
    student_id: Annotated[int, Depends(require_student_access)],
    service: Annotated[StudentUpcomingSessionService, Depends(get_student_upcoming_service)],
) -> UpcomingSessionResponse | None:
    try:
        return service.get_upcoming_session(student_id)
    except StudentGradeNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa có hồ sơ học sinh",
        ) from exc
