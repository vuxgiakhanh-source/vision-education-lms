from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_teacher_access
from app.database.database import DbSession

from ..repository import ScheduleAdjustmentRepository
from .schemas import SwapSessionsRequest
from .service import SwapSessionsService


swap_sessions_router = APIRouter()


def get_swap_sessions_service(db: DbSession) -> SwapSessionsService:
    return SwapSessionsService(ScheduleAdjustmentRepository(db))


@swap_sessions_router.put("/{session_id}/swap", status_code=status.HTTP_204_NO_CONTENT)
def confirm_swap_sessions(
    session_id: Annotated[int, Path(gt=0)],
    request: SwapSessionsRequest,
    teacher_id: Annotated[int, Depends(require_teacher_access)],
    service: Annotated[SwapSessionsService, Depends(get_swap_sessions_service)],
) -> None:
    service.swap_sessions(teacher_id, session_id, request)
