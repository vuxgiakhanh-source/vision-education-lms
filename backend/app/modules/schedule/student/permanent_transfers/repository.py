from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import Select, exists, func, or_, select, update
from sqlalchemy.orm import Session, SessionTransaction, aliased

from app.models.classroom import Class, ClassEnrollment
from app.models.schedule import ClassSession, SessionAttendance, SessionsTransfer


class PermanentTransferRepository:
    def __init__(self, db: Session):
        self.db = db

    def transaction(self) -> SessionTransaction:
        return self.db.begin()

    def get_current_enrollment(self, student_id: int, now: datetime) -> ClassEnrollment | None:
        statement = (
            select(ClassEnrollment)
            .where(ClassEnrollment.student_id == student_id, *self._enrollment_active_at(now))
            .order_by(ClassEnrollment.starts_at.desc(), ClassEnrollment.id.desc())
            .limit(1)
        )
        return self.db.scalar(statement)

    def lock_current_enrollment(
        self, student_id: int, enrollment_id: int, now: datetime
    ) -> ClassEnrollment | None:
        statement = (
            select(ClassEnrollment)
            .where(
                ClassEnrollment.id == enrollment_id,
                ClassEnrollment.student_id == student_id,
                *self._enrollment_active_at(now),
            )
            .with_for_update()
        )
        return self.db.scalar(statement)

    def get_class(self, class_id: int) -> Class | None:
        return self.db.get(Class, class_id)

    def lock_classes(self, class_ids: list[int]) -> dict[int, Class]:
        statement = (
            select(Class).where(Class.id.in_(class_ids)).order_by(Class.id).with_for_update()
        )
        return {classroom.id: classroom for classroom in self.db.scalars(statement)}

    def list_target_classes(self, source_class_id: int, grade: int, now: datetime) -> Sequence[Class]:
        statement = (
            select(Class)
            .where(Class.id != source_class_id, Class.grade == grade, *self._class_open_at(now))
            .order_by(Class.name, Class.id)
        )
        return self.db.scalars(statement).all()

    def get_enrollment_counts(self, class_ids: list[int], now: datetime) -> dict[int, int]:
        statement = (
            select(ClassEnrollment.class_id, func.count(ClassEnrollment.id))
            .where(ClassEnrollment.class_id.in_(class_ids), *self._enrollment_active_at(now))
            .group_by(ClassEnrollment.class_id)
        )
        return {class_id: count for class_id, count in self.db.execute(statement)}

    def get_first_sessions(
        self, class_ids: list[int], completed_through: int, now: datetime
    ) -> dict[int, ClassSession]:
        rank = func.row_number().over(
            partition_by=ClassSession.class_id,
            order_by=(ClassSession.starts_at, ClassSession.id),
        ).label("session_rank")
        ranked = self._eligible_sessions(class_ids, completed_through, now).add_columns(rank).subquery()
        session = aliased(ClassSession, ranked)
        return {
            row.class_id: row
            for row in self.db.scalars(select(session).where(ranked.c.session_rank == 1))
        }

    def lock_first_session(
        self, class_id: int, completed_through: int, now: datetime
    ) -> ClassSession | None:
        statement = (
            self._eligible_sessions([class_id], completed_through, now)
            .order_by(ClassSession.starts_at, ClassSession.id)
            .limit(1)
            .with_for_update()
        )
        return self.db.scalar(statement)

    def replace_enrollment(
        self,
        current: ClassEnrollment,
        target_class_id: int,
        now: datetime,
        completed_through: int,
        entry_session_id: int | None,
    ) -> ClassEnrollment:
        current.ends_at = now
        enrollment = ClassEnrollment(
            student_id=current.student_id,
            class_id=target_class_id,
            starts_at=now,
            completed_through_teaching_week=completed_through,
            entry_session_id=entry_session_id,
        )
        self.db.add(enrollment)
        self.db.flush()
        return enrollment

    def supersede_unfinished_temporary_transfers(self, student_id: int, now: datetime) -> None:
        attended = exists().where(
            SessionAttendance.student_id == student_id,
            SessionAttendance.session_id == ClassSession.id,
        )
        unfinished = select(ClassSession.id).where(ClassSession.ends_at > now, ~attended)
        self.db.execute(
            update(SessionsTransfer)
            .where(
                SessionsTransfer.student_id == student_id,
                SessionsTransfer.superseded_at.is_(None),
                SessionsTransfer.replacement_sessions_id.in_(unfinished),
            )
            .values(superseded_at=now)
        )

    @staticmethod
    def _enrollment_active_at(now: datetime):
        return (
            ClassEnrollment.starts_at <= now,
            or_(ClassEnrollment.ends_at.is_(None), ClassEnrollment.ends_at > now),
        )

    @staticmethod
    def _class_open_at(now: datetime):
        return (or_(Class.ends_at.is_(None), Class.ends_at > now),)

    @staticmethod
    def _eligible_sessions(
        class_ids: list[int], completed_through: int, now: datetime
    ) -> Select[tuple[ClassSession]]:
        return select(ClassSession).where(
            ClassSession.class_id.in_(class_ids),
            ClassSession.teaching_week > completed_through,
            ClassSession.status == "scheduled",
            ClassSession.ends_at > now,
        )
