from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_teacher_access
from app.database.database import DbSession

from ..repository import ScheduleAdjustmentRepository
from .schemas import MoveSessionRequest
from .service import MoveSessionService


move_session_router = APIRouter()


def get_move_session_service(db: DbSession) -> MoveSessionService:
    return MoveSessionService(ScheduleAdjustmentRepository(db))


@move_session_router.put("/{session_id}/move", status_code=status.HTTP_204_NO_CONTENT)
def confirm_move_session(
    session_id: Annotated[int, Path(gt=0)],
    request: MoveSessionRequest,
    teacher_id: Annotated[int, Depends(require_teacher_access)],
    service: Annotated[MoveSessionService, Depends(get_move_session_service)],
) -> None:
    service.move_session(teacher_id, session_id, request)
