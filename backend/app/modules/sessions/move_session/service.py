from datetime import datetime, time

from fastapi import HTTPException, status

from app.core import clock

from ..repository import ScheduleAdjustmentRepository
from ..schemas import SessionTime
from ..service import apply_schedule_change, matches_time, require_adjustable, scheduled_session
from .schemas import MoveSessionRequest


TEACHING_HOURS = {
    "morning": (time(7, 30), time(10, 30)),
    "afternoon": (time(14), time(17)),
    "evening": (time(18), time(21)),
}


class MoveSessionService:
    def __init__(self, repository: ScheduleAdjustmentRepository):
        self.repository = repository

    def move_session(self, teacher_id: int, session_id: int, request: MoveSessionRequest) -> None:
        start, end = TEACHING_HOURS[request.target_shift]
        target = SessionTime(
            starts_at=datetime.combine(request.target_date, start),
            ends_at=datetime.combine(request.target_date, end),
        )
        with self.repository.transaction():
            self.repository.lock_teacher(teacher_id)
            sessions = self.repository.lock_affected_class_sessions([session_id])
            session = scheduled_session(sessions, session_id)
            if matches_time(session, target):
                return

            now = clock.center_local_now()
            require_adjustable(self.repository, session, request.expected_time, now)
            if target.starts_at <= now:
                raise HTTPException(status.HTTP_409_CONFLICT, "Chọn một ca dạy chưa bắt đầu.")
            if self.repository.has_overlap(target.starts_at, target.ends_at, [session.id]):
                raise HTTPException(status.HTTP_409_CONFLICT, "Ca mới trùng giờ với một buổi dạy khác.")

            apply_schedule_change(self.repository, sessions, {session.id: target}, now)
