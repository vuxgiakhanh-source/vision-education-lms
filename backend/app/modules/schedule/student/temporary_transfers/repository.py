from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import Select, exists, or_, select
from sqlalchemy.orm import Session, SessionTransaction, aliased

from app.models.classroom import Class, ClassEnrollment
from app.models.schedule import ClassSession, SessionAttendance, SessionsTransfer

from ..repository import ScheduleWeekProgress


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
        transfer.requires_confirmation = False

    def list_pending_confirmations(
        self, student_id: int, grade: int, now: datetime, progress: ScheduleWeekProgress | None,
    ):
        statement = (
            self._confirmation_options(student_id, grade, now, progress)
            .where(SessionsTransfer.requires_confirmation.is_(True))
            .order_by(ClassSession.starts_at, ClassSession.id)
        )
        return self.db.execute(statement).all()

    def get_confirmation_option(
        self, student_id: int, grade: int, now: datetime, progress: ScheduleWeekProgress | None,
        original_id: int, target_id: int,
    ):
        return self.db.execute(
            self._confirmation_options(student_id, grade, now, progress).where(
                SessionsTransfer.original_session_id == original_id,
                ClassSession.id == target_id,
            )
        ).one_or_none()

    def _confirmation_options(
        self, student_id: int, grade: int, now: datetime, progress: ScheduleWeekProgress | None,
    ):
        original = aliased(ClassSession)
        attended = aliased(ClassSession)
        attended_class = aliased(Class)
        active_enrollment = exists().where(
            ClassEnrollment.student_id == student_id,
            ClassEnrollment.class_id == original.class_id,
            ClassEnrollment.starts_at <= now,
            or_(ClassEnrollment.ends_at.is_(None), ClassEnrollment.ends_at > now),
            or_(ClassEnrollment.starts_at <= original.starts_at, ClassEnrollment.entry_session_id == original.id),
            or_(
                ClassEnrollment.completed_through_teaching_week.is_(None),
                original.teaching_week > ClassEnrollment.completed_through_teaching_week,
            ),
        )
        if progress is not None:
            active_enrollment = active_enrollment.where(
                or_(ClassEnrollment.id != progress.enrollment_id, original.teaching_week > progress.completed_week)
            )
        attended_week = (
            select(SessionAttendance.session_id)
            .join(attended, attended.id == SessionAttendance.session_id)
            .join(attended_class, attended_class.id == attended.class_id)
            .where(
                SessionAttendance.student_id == student_id,
                attended_class.grade == grade,
                attended.teaching_week == original.teaching_week,
            )
            .exists()
        )
        return (
            select(SessionsTransfer, ClassSession, Class.name)
            .join(original, original.id == SessionsTransfer.original_session_id)
            .join(ClassSession, ClassSession.id == SessionsTransfer.replacement_sessions_id)
            .join(Class, Class.id == ClassSession.class_id)
            .where(
                SessionsTransfer.student_id == student_id,
                SessionsTransfer.superseded_at.is_(None),
                Class.grade == grade,
                ClassSession.teaching_week == original.teaching_week,
                ClassSession.status == "scheduled",
                ClassSession.ends_at >= now,
                active_enrollment,
                ~attended_week,
            )
        )

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
