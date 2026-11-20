from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_lms_access
from app.database.database import get_db

from ..exceptions import StudentGradeNotFoundException
from ..repository import ScheduleRepository
from .repository import PermanentTransferRepository
from .schemas import (
    ConfirmPermanentTransferRequest,
    ConfirmPermanentTransferResponse,
    PermanentTransferOptionsResponse,
)
from .service import PermanentTransferConflict, PermanentTransferService


permanent_transfer_router = APIRouter(prefix="/schedule/permanent-transfers")


def get_permanent_transfer_service(
    db: Annotated[Session, Depends(get_db)],
) -> PermanentTransferService:
    return PermanentTransferService(PermanentTransferRepository(db), ScheduleRepository(db))


@permanent_transfer_router.get("/options")
def get_permanent_transfer_options(
    student_id: Annotated[int, Depends(require_lms_access)],
    service: Annotated[PermanentTransferService, Depends(get_permanent_transfer_service)],
) -> PermanentTransferOptionsResponse:
    try:
        return service.get_options(student_id)
    except StudentGradeNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa có hồ sơ học sinh",
        ) from exc


@permanent_transfer_router.post("")
def confirm_permanent_transfer(
    request: ConfirmPermanentTransferRequest,
    student_id: Annotated[int, Depends(require_lms_access)],
    service: Annotated[PermanentTransferService, Depends(get_permanent_transfer_service)],
) -> ConfirmPermanentTransferResponse:
    try:
        return service.confirm_transfer(student_id, request)
    except StudentGradeNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa có hồ sơ học sinh",
        ) from exc
    except PermanentTransferConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.detail.model_dump(mode="json"),
        ) from exc
