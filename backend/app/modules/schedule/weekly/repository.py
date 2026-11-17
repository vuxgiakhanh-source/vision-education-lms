from datetime import datetime

from sqlalchemy.orm import Session

from app.models.classroom import Class
from app.models.schedule import ClassSession
from app.models.student import Student


class WeeklyScheduleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_student_grade(self, user_id: int) -> int | None:
        return (
            self.db.query(Student.grade)
            .filter(Student.user_id == user_id)
            .scalar()
        )

    def get_sessions_in_range(
        self,
        grade: int,
        starts_from: datetime,
        starts_before: datetime,
    ) -> list[ClassSession]:
        return (
            self.db.query(ClassSession)
            .join(Class, ClassSession.class_id == Class.id)
            .filter(
                Class.grade == grade,
                ClassSession.starts_at >= starts_from,
                ClassSession.starts_at < starts_before,
                ClassSession.status == "scheduled",
            )
            .order_by(ClassSession.starts_at, ClassSession.id)
            .all()
        )
