from datetime import date, datetime, time
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_serializer, field_validator, model_validator

from app.core.clock import CENTER_TZ, to_center_iso


MAX_SIGNED_INT = 2_147_483_647


class ExamDraftFields(BaseModel):
    paper_id: int | None = Field(default=None, gt=0, le=MAX_SIGNED_INT, strict=True)
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)] | None = None
    description: str | None = Field(default=None, max_length=200)
    opens_at: datetime | None = None
    closes_at: datetime | None = None
    schedule_inputs: dict[Literal["opens_at", "closes_at"], str] | None = None
    duration_minutes: int | None = Field(default=None, gt=0, le=MAX_SIGNED_INT, strict=True)

    @field_validator("opens_at", "closes_at")
    @classmethod
    def normalize_center_time(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        # Giờ không có offset được hiểu là giờ Việt Nam.
        if value.tzinfo is not None:
            try:
                value = value.astimezone(CENTER_TZ)
            except OverflowError as exc:
                raise ValueError("Thời gian nằm ngoài khoảng lưu trữ.") from exc
        if value.year < 1000:
            raise ValueError("Thời gian nằm ngoài khoảng lưu trữ.")
        # Cột MySQL DATETIME hiện lưu đến giây.
        return value.replace(tzinfo=None, microsecond=0)

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.opens_at is not None and self.closes_at is not None and self.opens_at >= self.closes_at:
            raise ValueError("Giờ đóng phải sau giờ mở kỳ thi.")
        for field, value in (self.schedule_inputs or {}).items():
            if getattr(self, field) is not None:
                raise ValueError("Chỉ lưu phần ngày hoặc giờ khi thời điểm chưa đầy đủ.")
            day, separator, clock = value.partition("T")
            if not separator or bool(day) == bool(clock):
                raise ValueError("Thời điểm đang nhập phải có ngày hoặc giờ.")
            if day:
                parsed = date.fromisoformat(day)
                if parsed.year < 1000 or parsed.isoformat() != day:
                    raise ValueError("Ngày nằm ngoài khoảng lưu trữ.")
            elif len(clock) != 5 or time.fromisoformat(clock).isoformat(timespec="minutes") != clock:
                raise ValueError("Giờ phải có dạng HH:MM.")
        return self


class CreateExamDraftRequest(ExamDraftFields):
    autosave_key: UUID | None = None


class UpdateExamDraftRequest(ExamDraftFields):
    version: int = Field(gt=0, strict=True)


class CreateExamDraftResponse(BaseModel):
    exam_id: int


class ExamDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    exam_id: int = Field(validation_alias="id")
    version: int
    autosave_key: str | None
    paper_id: int | None
    title: str | None
    description: str | None
    opens_at: datetime | None
    closes_at: datetime | None
    schedule_inputs: dict[str, str] | None
    duration_minutes: int | None

    @field_serializer("opens_at", "closes_at")
    def serialize_center_time(self, value: datetime | None) -> str | None:
        return to_center_iso(value) if value is not None else None
