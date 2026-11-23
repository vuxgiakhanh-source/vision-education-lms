from datetime import date

from pydantic import BaseModel

from app.modules.sessions.schemas import TeachingSessionResponse


class TeacherWeeklyScheduleResponse(BaseModel):
    week_start: date
    sessions: list[TeachingSessionResponse]
