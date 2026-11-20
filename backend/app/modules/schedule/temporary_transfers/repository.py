from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, SessionTransaction

from app.models.classroom import Class
from app.models.schedule import ClassSession, SessionsTransfer


class TemporaryTransferRepository:
    def __init__(self, db: Session):
        self.db = db

    def transaction(self) -> SessionTransaction:
        return self.db.begin()

    def lock_sessions(self, session_ids: Sequence[int]) -> None:
        statement = (
            select(ClassSession)
            .where(ClassSession.id.in_(session_ids))
            .order_by(ClassSession.id)
            .with_for_update()
        )
        self.db.scalars(statement).all()

    def set_replacement(
        self, student_id: int, original_session_id: int, replacement_session_id: int | None
    ) -> None:
        transfer = self.db.get(SessionsTransfer, (student_id, original_session_id))
        if transfer is None:
            transfer = SessionsTransfer(
                student_id=student_id, original_session_id=original_session_id
            )
            self.db.add(transfer)
        transfer.replacement_sessions_id = replacement_session_id
        transfer.superseded_at = None

    def list_replacement_sessions(
        self,
        *,
        grade: int,
        teaching_week: int | None,
        now: datetime,
        excluded_session_ids: Sequence[int],
    ) -> Sequence[ClassSession]:
        if teaching_week is None:
            return []

        statement = (
            self._replacement_sessions(grade, teaching_week, now)
            .where(ClassSession.id.not_in(excluded_session_ids))
            .order_by(ClassSession.starts_at, ClassSession.id)
        )
        return self.db.scalars(statement).all()

    def get_replacement_session(
        self, *, session_id: int, grade: int, teaching_week: int, now: datetime
    ) -> ClassSession | None:
        statement = self._replacement_sessions(grade, teaching_week, now).where(
            ClassSession.id == session_id
        )
        return self.db.scalars(statement).one_or_none()

    def _replacement_sessions(
        self, grade: int, teaching_week: int, now: datetime
    ) -> Select[tuple[ClassSession]]:
        return (
            select(ClassSession)
            .join(Class, ClassSession.class_id == Class.id)
            .where(
                Class.grade == grade,
                ClassSession.teaching_week == teaching_week,
                ClassSession.status == "scheduled",
                ClassSession.ends_at >= now,
            )
        )
