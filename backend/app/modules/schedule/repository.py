from collections.abc import Sequence
from datetime import datetime
from typing import NamedTuple
from sqlalchemy import Row, and_, exists, func, or_, select
from sqlalchemy.orm import Session, aliased
from app.models.classroom import Class, ClassEnrollment
from app.models.schedule import ClassSession, SessionAttendance, SessionsTransfer
from app.models.student import Student


class SessionAssignment(NamedTuple):
    original: ClassSession
    current: ClassSession
    enrollment_id: int


class ScheduleWeekProgress(NamedTuple):
    enrollment_id: int
    completed_week: int


class ScheduleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_student_grade(self, user_id: int) -> int | None:
        return (
            self.db.query(Student.grade)
            .filter(Student.user_id == user_id)
            .scalar()
        )

    def lock_student_grade(self, student_id: int) -> int | None:
        return self.db.scalar(
            select(Student.grade).where(Student.user_id == student_id).with_for_update()
        )

    def get_enrolled_session_ids(
        self, student_id: int, session_ids: list[int], progress: ScheduleWeekProgress | None
    ) -> set[int]:
        statement = (
            select(ClassSession.id)
            .join(ClassEnrollment, self._session_matches_enrollment(student_id, progress))
            .where(ClassSession.id.in_(session_ids))
        )
        return set(self.db.scalars(statement))

    def get_student_transfers_for_sessions(
        self, student_id: int, session_ids: list[int], progress: ScheduleWeekProgress | None
    ):
        statement = (
            select(SessionsTransfer)
            .where(
                SessionsTransfer.student_id == student_id,
                SessionsTransfer.replacement_sessions_id.is_not(None),
                SessionsTransfer.superseded_at.is_(None),
                or_(
                    SessionsTransfer.original_session_id.in_(session_ids),
                    SessionsTransfer.replacement_sessions_id.in_(session_ids),
                ),
            )
        )
        if progress is not None:
            completed_originals = (
                select(ClassSession.id)
                .join(ClassEnrollment, self._session_matches_enrollment(student_id, None))
                .where(~self._above_current_progress(progress))
            )
            statement = statement.where(SessionsTransfer.original_session_id.not_in(completed_originals))
        return self.db.scalars(statement).all()

    def has_student_attended(self, student_id: int, session_id: int) -> bool:
        statement = select(
            exists().where(
                SessionAttendance.student_id == student_id,
                SessionAttendance.session_id == session_id,
            )
        )
        return bool(self.db.scalar(statement))

    def get_relevant_attendances(
        self, student_id: int, grade: int, session_ids: list[int], teaching_weeks: set[int]
    ) -> Sequence[Row[tuple[int, int | None]]]:
        statement = self._attendance_for_grade(student_id, grade, ClassSession).where(
            or_(ClassSession.id.in_(session_ids), ClassSession.teaching_week.in_(teaching_weeks))
        )
        return self.db.execute(statement).all()

    def get_completed_through_week(self, student_id: int, grade: int) -> int | None:
        return self.db.scalar(self._max_attended_teaching_week(student_id, grade))

    def get_current_schedule_progress(
        self, student_id: int, grade: int, now: datetime
    ) -> ScheduleWeekProgress | None:
        statement = (
            select(ClassEnrollment.id, self._max_attended_teaching_week(student_id, grade).scalar_subquery())
            .where(
                ClassEnrollment.student_id == student_id,
                ClassEnrollment.completed_through_teaching_week.is_not(None),
                ClassEnrollment.starts_at <= now,
                or_(ClassEnrollment.ends_at.is_(None), ClassEnrollment.ends_at > now),
            )
            .order_by(ClassEnrollment.starts_at.desc(), ClassEnrollment.id.desc())
            .limit(1)
        )
        row = self.db.execute(statement).first()
        if row is None or row[1] is None:
            return None
        return ScheduleWeekProgress(*row)

    def _max_attended_teaching_week(self, student_id: int, grade: int):
        return self._attendance_for_grade(student_id, grade, ClassSession).with_only_columns(
            func.max(ClassSession.teaching_week)
        )

    @staticmethod
    def _attendance_for_grade(student_id: int, grade: int, session):
        classroom = aliased(Class)
        return (
            select(session.id, session.teaching_week)
            .select_from(SessionAttendance)
            .join(session, session.id == SessionAttendance.session_id)
            .join(classroom, classroom.id == session.class_id)
            .where(SessionAttendance.student_id == student_id, classroom.grade == grade)
        )

    @staticmethod
    def _above_current_progress(progress: ScheduleWeekProgress):
        return or_(
            ClassEnrollment.id != progress.enrollment_id,
            ClassSession.teaching_week > progress.completed_week,
        )

    def _session_matches_enrollment(self, student_id: int, progress: ScheduleWeekProgress | None):
        conditions = [
            ClassEnrollment.student_id == student_id,
            ClassEnrollment.class_id == ClassSession.class_id,
            or_(
                ClassEnrollment.starts_at <= ClassSession.starts_at,
                ClassEnrollment.entry_session_id == ClassSession.id,
            ),
            or_(
                ClassEnrollment.completed_through_teaching_week.is_(None),
                ClassSession.teaching_week > ClassEnrollment.completed_through_teaching_week,
            ),
            or_(
                ClassEnrollment.ends_at.is_(None),
                ClassEnrollment.ends_at >= ClassSession.ends_at,
                exists().where(
                    SessionAttendance.student_id == student_id,
                    SessionAttendance.session_id == ClassSession.id,
                    ClassSession.starts_at < ClassEnrollment.ends_at,
                ).correlate(ClassSession, ClassEnrollment),
            ),
        ]
        if progress is not None:
            conditions.append(self._above_current_progress(progress))
        return and_(*conditions)

    def get_first_unfinished_assignment(
        self, *, student_id: int, grade: int, now: datetime
    ) -> SessionAssignment | None:
        current_session = aliased(ClassSession)
        attended_session = aliased(ClassSession)
        progress = self.get_current_schedule_progress(student_id, grade, now)
        has_attended_teaching_week = (
            self._attendance_for_grade(student_id, grade, attended_session)
            .where(
                or_(
                    attended_session.id == current_session.id,
                    attended_session.teaching_week == ClassSession.teaching_week,
                ),
            )
            .exists()
        )
        statement = (
            select(ClassSession, current_session, ClassEnrollment.id)
            .join(Class, ClassSession.class_id == Class.id)
            .join(ClassEnrollment, self._session_matches_enrollment(student_id, progress))
            .outerjoin(
                SessionsTransfer,
                and_(
                    SessionsTransfer.original_session_id == ClassSession.id,
                    SessionsTransfer.student_id == student_id,
                    SessionsTransfer.superseded_at.is_(None),
                ),
            )
            .join(
                current_session,
                current_session.id
                == func.coalesce(SessionsTransfer.replacement_sessions_id, ClassSession.id),
            )
            .where(
                Class.grade == grade,
                ~has_attended_teaching_week,
                current_session.status == "scheduled",
                current_session.ends_at >= now,
                or_(ClassEnrollment.ends_at.is_(None), ClassEnrollment.ends_at > now),
            )
            .order_by(
                current_session.starts_at,
                current_session.id,
                ClassSession.id,
            )
            .limit(1)
        )
        row = self.db.execute(statement).first()
        return SessionAssignment(*row) if row is not None else None
