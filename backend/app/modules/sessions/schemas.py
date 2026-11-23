from datetime import datetime

from pydantic import BaseModel, ConfigDict, NaiveDatetime


class TeachingSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    class_name: str
    teaching_week: int | None
    topic: str
    starts_at: datetime
    ends_at: datetime


class SessionTime(BaseModel):
    starts_at: NaiveDatetime
    ends_at: NaiveDatetime
