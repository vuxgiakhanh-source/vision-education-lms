from datetime import date, timedelta
from typing import Literal

from pydantic import BaseModel, Field

from ..schemas import SessionTime


class MoveSessionRequest(BaseModel):
    expected_time: SessionTime
    target_date: date = Field(ge=date(1000, 1, 1), lt=date.max - timedelta(days=date.max.weekday()))
    target_shift: Literal["morning", "afternoon", "evening"]
