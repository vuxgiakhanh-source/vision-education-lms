from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import DbSession
from app.modules.sessions.repository import TeachingSessionRepository
from app.modules.sessions.schemas import TeachingSessionResponse

from .service import TeacherUpcomingSessionService


teacher_upcoming_router = APIRouter()


def get_teacher_upcoming_service(
    db: DbSession,
) -> TeacherUpcomingSessionService:
    return TeacherUpcomingSessionService(TeachingSessionRepository(db))


@teacher_upcoming_router.get("/schedule/upcoming")
def get_upcoming_session(
    service: Annotated[TeacherUpcomingSessionService, Depends(get_teacher_upcoming_service)],
) -> TeachingSessionResponse | None:
    return service.get_upcoming_session()
