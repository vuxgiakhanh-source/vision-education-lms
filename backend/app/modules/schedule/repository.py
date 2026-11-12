from sqlalchemy.orm import Session
from app.models.classroom import Class, ClassEnrollment
from app.models.schedule import ClassSession

class ScheduleRepository:
    def __init__(self, db: Session):
        self.db = db
    def get_student_upcoming_sessions(self, student_id: int, limit: int = 5):
        return (
            self.db.query(ClassSession)
            .filter
        )