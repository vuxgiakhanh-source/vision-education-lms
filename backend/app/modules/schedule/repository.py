from datetime import datetime, timedelta
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.classroom import Class, ClassEnrollment
from app.models.schedule import ClassSession, SessionsTransfer
from app.models.student import Student


class ScheduleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_student_grade(self, user_id: int):
        return (
            self.db.query(Student.grade)
            .filter(Student.user_id == user_id)
            .scalar()
        )
    def get_upcoming_sessions(self, grade: int, starts_from: datetime, limit: int = 5):
        return (
            self.db.query(ClassSession)
            .join(Class, ClassSession.class_id == Class.id)
            .filter(
                Class.grade == grade,
                ClassSession.starts_at >= starts_from,  
                ClassSession.status == "scheduled"
            )
            .order_by(ClassSession.starts_at, ClassSession.id)
            .limit(limit)
            .all()
        )
    def get_sessions_in_range(self, grade: int, starts_from: datetime, starts_before: datetime):
        return (
            self.db.query(ClassSession)
            .join(Class, ClassSession.class_id == Class.id)
            .filter(
                Class.grade == grade,
                ClassSession.starts_at >= starts_from,
                ClassSession.starts_at < starts_before,
                ClassSession.status == "scheduled"
            )
            .all()
        )
    def get_student_enrollments_in_range(self, student_id: int, starts_from: datetime, starts_before: datetime):
        return (
            self.db.query(ClassEnrollment)
            .filter(
                ClassEnrollment.student_id == student_id,
                ClassEnrollment.starts_at < starts_before,
                or_(
                    ClassEnrollment.ends_at.is_(None),
                    ClassEnrollment.ends_at > starts_from,
                )
            )
            .all()
        )
    def get_student_transfers_for_sessions(
        self, student_id: int, session_ids: list[int]
    ):
        return (
            self.db.query(SessionsTransfer)
            .filter(
                SessionsTransfer.student_id == student_id,
                SessionsTransfer.replacement_sessions_id.is_not(None),
                or_(
                    SessionsTransfer.original_session_id.in_(session_ids),
                    SessionsTransfer.replacement_sessions_id.in_(session_ids),
                ),
            )
            .all()
        )