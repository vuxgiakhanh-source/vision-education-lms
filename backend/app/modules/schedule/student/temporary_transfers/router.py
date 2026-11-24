from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import PositiveInt
from sqlalchemy.orm import Session

from app.core.dependencies import require_student_access
from app.database.database import DbSession

from ..exceptions import StudentGradeNotFoundException
from ..repository import ScheduleRepository
from .repository import TemporaryTransferRepository
from .schemas import (
    ConfirmChangedTransferRequest,
    ConfirmTemporaryTransferRequest,
    ConfirmTemporaryTransferResponse,
    PendingTemporaryTransfer,
    TemporaryTransferOptionsResponse,
)
from .service import TemporaryTransferConflict, TemporaryTransferService


temporary_transfer_router = APIRouter()


def get_temporary_transfer_service(
    db: DbSession,
) -> TemporaryTransferService:
    return TemporaryTransferService(TemporaryTransferRepository(db), ScheduleRepository(db))


@temporary_transfer_router.get("/schedule/temporary-transfers/pending")
def get_pending_temporary_transfers(
    student_id: Annotated[int, Depends(require_student_access)],
    service: Annotated[TemporaryTransferService, Depends(get_temporary_transfer_service)],
) -> list[PendingTemporaryTransfer]:
    try:
        return service.get_pending_confirmations(student_id)
    except StudentGradeNotFoundException as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tài khoản chưa có hồ sơ học sinh") from exc


@temporary_transfer_router.put(
    "/schedule/temporary-transfers/{original_session_id}/reconfirm",
    status_code=status.HTTP_204_NO_CONTENT,
)
def reconfirm_temporary_transfer(
    original_session_id: PositiveInt,
    request: ConfirmChangedTransferRequest,
    student_id: Annotated[int, Depends(require_student_access)],
    service: Annotated[TemporaryTransferService, Depends(get_temporary_transfer_service)],
) -> None:
    try:
        service.confirm_changed_transfer(student_id, original_session_id, request)
    except StudentGradeNotFoundException as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tài khoản chưa có hồ sơ học sinh") from exc
    except TemporaryTransferConflict as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT, exc.detail.model_dump(mode="json", exclude_none=True)
        ) from exc


@temporary_transfer_router.get(
    "/schedule/temporary-transfers/options", response_model=TemporaryTransferOptionsResponse
)
def get_temporary_transfer_options(
    student_id: Annotated[int, Depends(require_student_access)],
    service: Annotated[TemporaryTransferService, Depends(get_temporary_transfer_service)],
) -> TemporaryTransferOptionsResponse:
    try:
        return service.get_options(student_id)
    except StudentGradeNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa có hồ sơ học sinh",
        ) from exc


@temporary_transfer_router.put(
    "/schedule/temporary-transfers/{original_session_id}",
    response_model=ConfirmTemporaryTransferResponse,
)
def confirm_temporary_transfer(
    original_session_id: PositiveInt,
    request: ConfirmTemporaryTransferRequest,
    student_id: Annotated[int, Depends(require_student_access)],
    service: Annotated[TemporaryTransferService, Depends(get_temporary_transfer_service)],
) -> ConfirmTemporaryTransferResponse:
    try:
        return service.confirm_transfer(student_id, original_session_id, request)
    except StudentGradeNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa có hồ sơ học sinh",
        ) from exc
    except TemporaryTransferConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.detail.model_dump(mode="json", exclude_none=True),
        ) from exc
