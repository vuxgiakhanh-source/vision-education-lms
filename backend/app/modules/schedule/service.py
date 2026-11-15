from .exceptions import (
    StudentGradeNotFoundException
)
from datetime import datetime, timedelta

from .repository import ScheduleRepository

class ScheduleService:
    def __init__(self, repository: ScheduleRepository):
        self.repository = repository
    def get_weekly_sessions(self, user_id: int, week_start: datetime):
        grade = self.repository.get_student_grade(user_id)
        if grade is None:
            raise StudentGradeNotFoundException()
        week_end = week_start + timedelta(days=7)
        return self.repository.get_sessions_in_range(grade, week_start, week_end)
