from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class WeeklySessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic: str
    starts_at: datetime
    ends_at: datetime


class WeeklyScheduleResponse(BaseModel):
    week_start: date
    sessions: list[WeeklySessionResponse]
    my_session_ids: list[int]
    transferred_session_ids: list[int]
