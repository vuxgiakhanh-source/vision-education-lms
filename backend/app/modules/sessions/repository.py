from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import Row, exists, select, update
from sqlalchemy.orm import Session, SessionTransaction, aliased

from app.models.classroom import Class
from app.models.schedule import ClassSession, SessionAttendance, SessionsTransfer
from app.models.user import User


class TeachingSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def _scheduled_sessions(self):
        return (
            select(
                ClassSession.id,
                Class.name.label("class_name"),
                ClassSession.teaching_week,
                ClassSession.topic,
                ClassSession.starts_at,
                ClassSession.ends_at,
            )
            .join(Class, ClassSession.class_id == Class.id)
            .where(ClassSession.status == "scheduled")
        )

    def get_sessions_in_range(self, starts_from: datetime, starts_before: datetime) -> Sequence[Row]:
        statement = (
            self._scheduled_sessions()
            .where(ClassSession.starts_at >= starts_from, ClassSession.starts_at < starts_before)
            .order_by(ClassSession.starts_at, ClassSession.id)
        )
        return self.db.execute(statement).all()

    def get_next_session(self, now: datetime) -> Row | None:
        statement = (
            self._scheduled_sessions()
            .where(ClassSession.starts_at >= now)
            .order_by(ClassSession.starts_at, ClassSession.id)
            .limit(1)
        )
        return self.db.execute(statement).one_or_none()

    def get_session(self, session_id: int) -> Row | None:
        statement = self._scheduled_sessions().where(ClassSession.id == session_id)
        return self.db.execute(statement).one_or_none()


class ScheduleAdjustmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def transaction(self) -> SessionTransaction:
        return self.db.begin()

    def lock_teacher(self, teacher_id: int) -> None:
        # Both adjustment endpoints serialize writes for the center's sole teacher.
        self.db.scalar(select(User.id).where(User.id == teacher_id).with_for_update())

    def lock_affected_class_sessions(self, session_ids: Sequence[int]) -> dict[int, ClassSession]:
        selected = aliased(ClassSession)
        class_ids = select(selected.class_id).where(selected.id.in_(session_ids))
        sessions = self.db.scalars(
            select(ClassSession).where(
                ClassSession.class_id.in_(class_ids),
                ClassSession.status == "scheduled",
            )
            .order_by(ClassSession.id).with_for_update()
        )
        return {session.id: session for session in sessions}

    def has_attendance(self, session_id: int) -> bool:
        return self.db.scalar(
            select(SessionAttendance.session_id)
            .where(SessionAttendance.session_id == session_id)
            .limit(1)
            .with_for_update()
        ) is not None

    def require_transfer_confirmation(self, session_ids: Sequence[int]) -> None:
        self.db.execute(
            update(SessionsTransfer)
            .where(
                SessionsTransfer.replacement_sessions_id.in_(session_ids),
                SessionsTransfer.superseded_at.is_(None),
            )
            .values(requires_confirmation=True)
        )

    def has_overlap(
        self, starts_at: datetime, ends_at: datetime, excluded_ids: Sequence[int]
    ) -> bool:
        return bool(self.db.scalar(select(exists().where(
            ClassSession.status == "scheduled",
            ClassSession.id.not_in(excluded_ids),
            ClassSession.starts_at < ends_at,
            ClassSession.ends_at > starts_at,
        ))))
