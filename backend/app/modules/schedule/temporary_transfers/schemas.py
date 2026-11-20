from datetime import datetime
from typing import Literal

from pydantic import BaseModel, NaiveDatetime, PositiveInt


class TemporaryTransferSource(BaseModel):
    enrollment_id: int
    original_session_id: int
    current_session_id: int
    teaching_week: int | None
    topic: str
    starts_at: datetime
    ends_at: datetime


class TemporaryTransferOption(BaseModel):
    session_id: int
    starts_at: datetime
    ends_at: datetime


class TemporaryTransferOptionsResponse(BaseModel):
    source: TemporaryTransferSource | None
    options: list[TemporaryTransferOption]
    blocked_reason: Literal[
        "NO_UPCOMING_SESSION", "MISSING_TEACHING_WEEK", "NO_ELIGIBLE_SESSIONS"
    ] | None


class ConfirmTemporaryTransferRequest(BaseModel):
    expected_enrollment_id: PositiveInt
    expected_current_session_id: PositiveInt
    target_session_id: PositiveInt
    expected_target_starts_at: NaiveDatetime
    expected_target_ends_at: NaiveDatetime


class ConfirmTemporaryTransferResponse(BaseModel):
    original_session_id: int
    current_session_id: int


class TemporaryTransferConflictDetail(BaseModel):
    code: Literal["SOURCE_CHANGED", "ALREADY_PRESENT", "TARGET_UNAVAILABLE", "SESSION_TIME_CHANGED"]
    option: TemporaryTransferOption | None = None
