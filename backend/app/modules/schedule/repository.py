from datetime import datetime
from sqlalchemy.orm import Session
from app.models.classroom import Class, ClassEnrollment
from app.models.schedule import ClassSession
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
                Class.Session.starts_at > starts_from,
                Class.Session.starts_at < starts_before,
                ClassSession.status == "scheduled"
            )
            
        )