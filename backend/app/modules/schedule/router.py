from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_lms_access
from app.database.database import get_db

from .exceptions import StudentGradeNotFoundException
from .repository import ScheduleRepository
from .schemas import UpcomingSessionResponse
from .service import ScheduleService


schedule_router = APIRouter()


def get_schedule_service(db: Annotated[Session, Depends(get_db)]) -> ScheduleService:
    return ScheduleService(ScheduleRepository(db))


@schedule_router.get("/schedule/upcoming")
def get_upcoming_session(
    student_id: Annotated[int, Depends(require_lms_access)],
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> UpcomingSessionResponse | None:
    try:
        return service.get_upcoming_session(student_id)
    except StudentGradeNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa có hồ sơ học sinh",
        ) from exc
