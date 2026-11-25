from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from fastapi.routing import APIRoute

from app.core.dependencies import require_teacher_access
from app.database.database import DbSession
from app.modules.exams.exam_bank.repository import ExamBankRepository

from .exceptions import DraftConflictError, DraftGoneError, DraftNotFoundError
from .repository import ExamDraftRepository
from .schemas import CreateExamDraftRequest, CreateExamDraftResponse, ExamDraftResponse, UpdateExamDraftRequest
from .service import ExamDraftService


class DraftRoute(APIRoute):
    def get_route_handler(self):
        handle = super().get_route_handler()

        async def handle_draft(request: Request):
            try:
                return await handle(request)
            except DraftNotFoundError as error:
                raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
            except DraftConflictError as error:
                raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
            except DraftGoneError as error:
                raise HTTPException(status.HTTP_410_GONE, str(error)) from error

        return handle_draft


exam_drafts_router = APIRouter(prefix="/teacher/exams", route_class=DraftRoute)


def get_exam_draft_service(db: DbSession) -> ExamDraftService:
    return ExamDraftService(ExamDraftRepository(db), ExamBankRepository(db))


@exam_drafts_router.post("", status_code=status.HTTP_201_CREATED)
def create_exam_draft(
    request: CreateExamDraftRequest,
    teacher_id: Annotated[int, Depends(require_teacher_access)],
    service: Annotated[ExamDraftService, Depends(get_exam_draft_service)],
) -> CreateExamDraftResponse:
    return CreateExamDraftResponse(exam_id=service.create_draft(teacher_id, request))


@exam_drafts_router.get("/drafts")
def list_exam_drafts(
    teacher_id: Annotated[int, Depends(require_teacher_access)],
    service: Annotated[ExamDraftService, Depends(get_exam_draft_service)],
) -> list[ExamDraftResponse]:
    return service.list_drafts(teacher_id)


@exam_drafts_router.get("/drafts/by-key/{autosave_key}")
def get_exam_draft_by_autosave_key(
    autosave_key: UUID,
    teacher_id: Annotated[int, Depends(require_teacher_access)],
    service: Annotated[ExamDraftService, Depends(get_exam_draft_service)],
) -> ExamDraftResponse:
    return service.get_draft_by_autosave_key(teacher_id, str(autosave_key))


@exam_drafts_router.get("/{exam_id}")
def get_exam_draft(
    exam_id: Annotated[int, Path(gt=0)],
    teacher_id: Annotated[int, Depends(require_teacher_access)],
    service: Annotated[ExamDraftService, Depends(get_exam_draft_service)],
) -> ExamDraftResponse:
    return service.get_draft(teacher_id, exam_id)


@exam_drafts_router.put("/{exam_id}")
def update_exam_draft(
    exam_id: Annotated[int, Path(gt=0)],
    request: UpdateExamDraftRequest,
    teacher_id: Annotated[int, Depends(require_teacher_access)],
    service: Annotated[ExamDraftService, Depends(get_exam_draft_service)],
) -> ExamDraftResponse:
    return service.update_draft(teacher_id, exam_id, request)


@exam_drafts_router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam_draft(
    exam_id: Annotated[int, Path(gt=0)],
    teacher_id: Annotated[int, Depends(require_teacher_access)],
    service: Annotated[ExamDraftService, Depends(get_exam_draft_service)],
) -> None:
    service.delete_draft(teacher_id, exam_id)
