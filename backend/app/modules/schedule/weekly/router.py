from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_lms_access
from app.database.database import get_db

from ..exceptions import StudentGradeNotFoundException
from ..repository import ScheduleRepository
from .repository import WeeklyScheduleRepository
from .schemas import WeeklyScheduleResponse
from .service import WeeklyScheduleService


weekly_schedule_router = APIRouter()


def get_weekly_schedule_service(db: Annotated[Session, Depends(get_db)]) -> WeeklyScheduleService:
    return WeeklyScheduleService(WeeklyScheduleRepository(db), ScheduleRepository(db))


@weekly_schedule_router.get("/schedule/weekly", response_model=WeeklyScheduleResponse)
def get_weekly_schedule(
    week_start: Annotated[date, Query(lt=date.max - timedelta(days=date.max.weekday()))],
    user_id: Annotated[int, Depends(require_lms_access)],
    service: Annotated[WeeklyScheduleService, Depends(get_weekly_schedule_service)],
) -> WeeklyScheduleResponse:
    try:
        return service.get_weekly_sessions(user_id, week_start)
    except StudentGradeNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa có hồ sơ học sinh",
        ) from exc
