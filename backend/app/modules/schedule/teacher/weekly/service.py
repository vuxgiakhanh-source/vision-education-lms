from datetime import date, datetime, time, timedelta

from app.modules.sessions.repository import TeachingSessionRepository
from app.modules.sessions.schemas import TeachingSessionResponse

from .schemas import TeacherWeeklyScheduleResponse


class TeacherWeeklyScheduleService:
    def __init__(self, repository: TeachingSessionRepository):
        self.repository = repository

    def get_weekly_sessions(self, selected_date: date) -> TeacherWeeklyScheduleResponse:
        week_start = selected_date - timedelta(days=selected_date.weekday())
        starts_from = datetime.combine(week_start, time.min)
        sessions = self.repository.get_sessions_in_range(starts_from, starts_from + timedelta(days=7))
        return TeacherWeeklyScheduleResponse(
            week_start=week_start,
            sessions=[TeachingSessionResponse.model_validate(session) for session in sessions],
        )
