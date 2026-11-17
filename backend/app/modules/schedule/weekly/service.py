from datetime import date, datetime, time, timedelta

from ..exceptions import StudentGradeNotFoundException
from ..repository import ScheduleRepository
from .repository import WeeklyScheduleRepository
from .schemas import WeeklyScheduleResponse


class WeeklyScheduleService:
    def __init__(
        self,
        repository: WeeklyScheduleRepository,
        schedule_repository: ScheduleRepository,
    ):
        self.repository = repository
        self.schedule_repository = schedule_repository

    def get_weekly_sessions(self, user_id: int, selected_date: date) -> WeeklyScheduleResponse:
        grade = self.repository.get_student_grade(user_id)
        if grade is None:
            raise StudentGradeNotFoundException()

        monday = selected_date - timedelta(days=selected_date.weekday())
        week_start = datetime.combine(monday, time.min)
        week_end = week_start + timedelta(days=7)
        sessions = self.repository.get_sessions_in_range(grade, week_start, week_end)
        if not sessions:
            return WeeklyScheduleResponse(
                week_start=monday, sessions=[], my_session_ids=[], transferred_session_ids=[]
            )

        student_enrollments = self.schedule_repository.get_student_enrollments_in_range(
            user_id, week_start, week_end
        )
        student_transfers = self.schedule_repository.get_student_transfers_for_sessions(
            user_id, [session.id for session in sessions]
        )
        original_ids = {transfer.original_session_id for transfer in student_transfers}
        replacement_ids = {transfer.replacement_sessions_id for transfer in student_transfers}

        my_session_ids = []
        transferred_session_ids = []
        for session in sessions:
            if session.id in original_ids:
                transferred_session_ids.append(session.id)
            elif session.id in replacement_ids or any(
                enrollment.class_id == session.class_id
                and enrollment.starts_at <= session.starts_at
                and (enrollment.ends_at is None or session.starts_at < enrollment.ends_at)
                for enrollment in student_enrollments
            ):
                my_session_ids.append(session.id)

        return WeeklyScheduleResponse(
            week_start=monday,
            sessions=sessions,
            my_session_ids=my_session_ids,
            transferred_session_ids=transferred_session_ids,
        )
