from datetime import date, datetime, time, timedelta

from app.core import clock
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
        grade = self.schedule_repository.get_student_grade(user_id)
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

        session_ids = [session.id for session in sessions]
        progress = self.schedule_repository.get_current_schedule_progress(user_id, grade, clock.center_local_now())
        enrolled_ids = self.schedule_repository.get_enrolled_session_ids(user_id, session_ids, progress)
        student_transfers = self.schedule_repository.get_student_transfers_for_sessions(user_id, session_ids, progress)
        original_ids = {transfer.original_session_id for transfer in student_transfers}
        replacement_ids = {transfer.replacement_sessions_id for transfer in student_transfers}
        teaching_weeks = {session.teaching_week for session in sessions if session.teaching_week is not None}
        attendance = self.schedule_repository.get_relevant_attendances(user_id, grade, session_ids, teaching_weeks)
        attended_ids = {session_id for session_id, _ in attendance}
        attended_weeks = {week for _, week in attendance if week is not None}
        assigned_ids = enrolled_ids | replacement_ids

        my_session_ids = []
        transferred_session_ids = []
        for session in sessions:
            if session.id in attended_ids:
                my_session_ids.append(session.id)
            elif session.id in original_ids:
                transferred_session_ids.append(session.id)
            elif session.id in assigned_ids and session.teaching_week not in attended_weeks:
                my_session_ids.append(session.id)

        return WeeklyScheduleResponse(
            week_start=monday,
            sessions=sessions,
            my_session_ids=my_session_ids,
            transferred_session_ids=transferred_session_ids,
        )
