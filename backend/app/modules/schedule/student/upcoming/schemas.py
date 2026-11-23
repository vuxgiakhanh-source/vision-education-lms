from datetime import datetime

from pydantic import BaseModel


class UpcomingSessionResponse(BaseModel):
    grade: int
    topic: str
    starts_at: datetime
    ends_at: datetime
