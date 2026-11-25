from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, SessionTransaction

from app.models.exam import Exam


class ExamDraftRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def transaction(self) -> SessionTransaction:
        return self.db.begin()

    def add(self, exam: Exam) -> int:
        self.db.add(exam)
        self.db.flush()
        return exam.id

    def list_drafts(self, teacher_id: int) -> Sequence[Exam]:
        return self.db.scalars(self._active_drafts(teacher_id).order_by(Exam.id.desc())).all()

    def get_draft(self, teacher_id: int, exam_id: int, *, for_update: bool = False) -> Exam | None:
        statement = select(Exam).where(Exam.id == exam_id, Exam.created_by == teacher_id, Exam.status == "draft")
        if for_update:
            statement = statement.with_for_update()
        return self.db.scalar(statement)

    def get_by_autosave_key(self, teacher_id: int, key: str) -> Exam | None:
        return self.db.scalar(select(Exam).where(Exam.created_by == teacher_id, Exam.autosave_key == key))

    def _active_drafts(self, teacher_id: int):
        return select(Exam).where(
            Exam.created_by == teacher_id,
            Exam.status == "draft",
            Exam.discarded_at.is_(None),
        )
