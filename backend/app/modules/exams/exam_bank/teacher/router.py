from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import require_teacher_access
from app.database.database import DbSession

from ..repository import ExamBankRepository


class ExamPaperChoice(BaseModel):
    paper_id: int
    title: str


exam_bank_router = APIRouter(prefix="/teacher/exam-bank")


@exam_bank_router.get("/papers")
def list_exam_paper_choices(
    teacher_id: Annotated[int, Depends(require_teacher_access)],
    db: DbSession,
) -> list[ExamPaperChoice]:
    repository = ExamBankRepository(db)
    return [
        ExamPaperChoice(paper_id=paper_id, title=title)
        for paper_id, title in repository.list_owned_choices(teacher_id)
    ]
