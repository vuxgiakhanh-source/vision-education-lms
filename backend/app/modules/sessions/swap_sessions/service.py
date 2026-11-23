from fastapi import HTTPException, status

from app.core import clock

from ..repository import ScheduleAdjustmentRepository
from ..schemas import SessionTime
from ..service import apply_schedule_change, matches_time, require_adjustable, scheduled_session
from .schemas import SwapSessionsRequest


class SwapSessionsService:
    def __init__(self, repository: ScheduleAdjustmentRepository):
        self.repository = repository

    def swap_sessions(self, teacher_id: int, session_id: int, request: SwapSessionsRequest) -> None:
        other_id = request.other_session_id
        if session_id == other_id:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Chọn hai buổi dạy khác nhau.")

        session_ids = [session_id, other_id]
        with self.repository.transaction():
            self.repository.lock_teacher(teacher_id)
            sessions = self.repository.lock_affected_class_sessions(session_ids)
            source = scheduled_session(sessions, session_id)
            other = scheduled_session(sessions, other_id)
            if matches_time(source, request.expected_other_time) and matches_time(other, request.expected_time):
                return

            now = clock.center_local_now()
            require_adjustable(self.repository, source, request.expected_time, now)
            require_adjustable(self.repository, other, request.expected_other_time, now)
            if (
                (source.starts_at < other.ends_at and other.starts_at < source.ends_at)
                or self.repository.has_overlap(source.starts_at, source.ends_at, session_ids)
                or self.repository.has_overlap(other.starts_at, other.ends_at, session_ids)
            ):
                raise HTTPException(status.HTTP_409_CONFLICT, "Lịch sau khi hoán đổi bị trùng giờ.")

            apply_schedule_change(self.repository, sessions, {
                source.id: SessionTime(starts_at=other.starts_at, ends_at=other.ends_at),
                other.id: SessionTime(starts_at=source.starts_at, ends_at=source.ends_at),
            }, now)
