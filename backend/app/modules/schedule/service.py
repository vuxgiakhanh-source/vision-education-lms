from datetime import datetime, timedelta, timezone

from .exceptions import StudentGradeNotFoundException
from .repository import ScheduleRepository
from .schemas import UpcomingSessionResponse


def schedule_now() -> datetime:
    # ClassSession stores the center's Vietnam wall time without a UTC offset.
    return datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)


class ScheduleService:
    def __init__(self, repository: ScheduleRepository):
        self.repository = repository

    def get_upcoming_session(self, student_id: int) -> UpcomingSessionResponse | None:
        grade = self.repository.get_student_grade(student_id)
        if grade is None:
            raise StudentGradeNotFoundException()

        assignment = self.repository.get_first_unfinished_assignment(
            student_id=student_id, grade=grade, now=schedule_now()
        )
        if assignment is None:
            return None

        current = assignment.current
        return UpcomingSessionResponse(
            grade=grade, topic=current.topic, starts_at=current.starts_at, ends_at=current.ends_at
        )
