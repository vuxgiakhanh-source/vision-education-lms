from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.modules.sessions.repository import TeachingSessionRepository

from .schemas import TeacherWeeklyScheduleResponse
from .service import TeacherWeeklyScheduleService


weekly_router = APIRouter()


def get_teacher_weekly_service(
    db: Annotated[Session, Depends(get_db)],
) -> TeacherWeeklyScheduleService:
    return TeacherWeeklyScheduleService(TeachingSessionRepository(db))


@weekly_router.get("/schedule/weekly")
def get_weekly_schedule(
    week_start: Annotated[date, Query(lt=date.max - timedelta(days=date.max.weekday()))],
    service: Annotated[TeacherWeeklyScheduleService, Depends(get_teacher_weekly_service)],
) -> TeacherWeeklyScheduleResponse:
    return service.get_weekly_sessions(week_start)
