from collections import defaultdict
from datetime import datetime

from fastapi import HTTPException, status

from app.models.schedule import ClassSession

from .repository import ScheduleAdjustmentRepository, TeachingSessionRepository
from .schemas import SessionTime, TeachingSessionResponse


class TeachingSessionService:
    def __init__(self, repository: TeachingSessionRepository):
        self.repository = repository

    def get_session_detail(self, session_id: int) -> TeachingSessionResponse | None:
        session = self.repository.get_session(session_id)
        return TeachingSessionResponse.model_validate(session) if session is not None else None


def scheduled_session(sessions: dict[int, ClassSession], session_id: int) -> ClassSession:
    session = sessions.get(session_id)
    if session is None or session.status != "scheduled":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Buổi dạy không còn trong lịch.")
    return session


def matches_time(session: ClassSession, expected: SessionTime) -> bool:
    return session.starts_at == expected.starts_at and session.ends_at == expected.ends_at


def require_adjustable(
    repository: ScheduleAdjustmentRepository, session: ClassSession, expected: SessionTime, now: datetime
) -> None:
    if not matches_time(session, expected):
        raise HTTPException(status.HTTP_409_CONFLICT, {
            "code": "SESSION_TIME_CHANGED",
            "message": "Giờ buổi dạy đã thay đổi. Tải lại lịch trước khi xác nhận.",
        })
    require_upcoming(repository, session, now)


def require_upcoming(repository: ScheduleAdjustmentRepository, session: ClassSession, now: datetime) -> None:
    if session.starts_at <= now or repository.has_attendance(session.id):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Buổi dạy đã bắt đầu hoặc đã có điểm danh."
        )


def apply_schedule_change(
    repository: ScheduleAdjustmentRepository,
    sessions: dict[int, ClassSession],
    requested_slots: dict[int, SessionTime],
    now: datetime,
) -> None:
    # Session IDs identify lesson content and are referenced by transfers and attendance.
    slots = dict(requested_slots)
    affected_classes = {sessions[session_id].class_id for session_id in requested_slots}
    lessons_by_class: dict[int, list[ClassSession]] = defaultdict(list)
    for session in sessions.values():
        if session.class_id in affected_classes and session.teaching_week is not None:
            lessons_by_class[session.class_id].append(session)

    for lessons in lessons_by_class.values():
        lessons.sort(key=lambda lesson: (lesson.teaching_week, lesson.starts_at, lesson.id))
        ordered_slots = sorted(
            (slots.get(lesson.id) or SessionTime(starts_at=lesson.starts_at, ends_at=lesson.ends_at) for lesson in lessons),
            key=lambda slot: (slot.starts_at, slot.ends_at),
        )
        for lesson, slot in zip(lessons, ordered_slots, strict=True):
            slots[lesson.id] = slot

    changed = [session_id for session_id, slot in slots.items() if not matches_time(sessions[session_id], slot)]
    for session_id in changed:
        require_upcoming(repository, sessions[session_id], now)
        if slots[session_id].starts_at <= now:
            raise HTTPException(status.HTTP_409_CONFLICT, "Lịch mới ảnh hưởng đến buổi dạy đã bắt đầu.")

    for session_id in changed:
        sessions[session_id].starts_at = slots[session_id].starts_at
        sessions[session_id].ends_at = slots[session_id].ends_at
    if changed:
        repository.require_transfer_confirmation(changed)
