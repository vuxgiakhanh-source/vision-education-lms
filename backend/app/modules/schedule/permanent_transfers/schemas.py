from typing import Literal

from pydantic import BaseModel, NaiveDatetime, PositiveInt


class FirstSessionSnapshot(BaseModel):
    session_id: PositiveInt
    teaching_week: PositiveInt
    starts_at: NaiveDatetime
    ends_at: NaiveDatetime


class FirstSession(FirstSessionSnapshot):
    topic: str


class TransferClass(BaseModel):
    class_id: int
    class_name: str


class PermanentTransferOption(TransferClass):
    is_full: bool
    first_session: FirstSession | None


class PermanentTransferOptionsResponse(BaseModel):
    current_class: TransferClass | None
    current_enrollment_id: int | None
    completed_through_teaching_week: int | None
    options: list[PermanentTransferOption]


class ConfirmPermanentTransferRequest(BaseModel):
    target_class_id: PositiveInt
    expected_current_enrollment_id: PositiveInt
    expected_first_session: FirstSessionSnapshot | None


class ConfirmPermanentTransferResponse(BaseModel):
    new_class: TransferClass
    enrollment_id: int
    transferred_at: NaiveDatetime
    first_session: FirstSession | None


class PermanentTransferConflictDetail(BaseModel):
    code: Literal["SOURCE_CHANGED", "TARGET_UNAVAILABLE", "CLASS_FULL", "FIRST_SESSION_CHANGED"]
    first_session: FirstSession | None = None
