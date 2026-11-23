from app.models.classroom import Class
from app.models.schedule import ClassSession

from app.core import clock
from ..exceptions import StudentGradeNotFoundException
from ..repository import ScheduleRepository
from .repository import PermanentTransferRepository
from .schemas import (
    ConfirmPermanentTransferRequest,
    ConfirmPermanentTransferResponse,
    FirstSession,
    FirstSessionSnapshot,
    PermanentTransferConflictDetail,
    PermanentTransferOption,
    PermanentTransferOptionsResponse,
    TransferClass,
)


class PermanentTransferConflict(Exception):
    def __init__(self, detail: PermanentTransferConflictDetail):
        super().__init__(detail.code)
        self.detail = detail


def _transfer_class(classroom: Class) -> TransferClass:
    return TransferClass(class_id=classroom.id, class_name=classroom.name)


def _first_session(session: ClassSession | None) -> FirstSession | None:
    if session is None:
        return None
    return FirstSession(
        session_id=session.id,
        teaching_week=session.teaching_week,
        topic=session.topic,
        starts_at=session.starts_at,
        ends_at=session.ends_at,
    )


class PermanentTransferService:
    def __init__(self, repository: PermanentTransferRepository, schedule_repository: ScheduleRepository):
        self.repository = repository
        self.schedule_repository = schedule_repository

    def get_options(self, student_id: int) -> PermanentTransferOptionsResponse:
        grade = self.schedule_repository.get_student_grade(student_id)
        if grade is None:
            raise StudentGradeNotFoundException()

        now = clock.center_local_now()
        current = self.repository.get_current_enrollment(student_id, now)
        completed_through = self.schedule_repository.get_completed_through_week(student_id, grade)
        if current is None:
            return PermanentTransferOptionsResponse(
                current_class=None,
                current_enrollment_id=None,
                completed_through_teaching_week=completed_through,
                options=[],
            )

        current_class = self.repository.get_class(current.class_id)
        classroom_options = self.repository.list_target_classes(current.class_id, grade, now)
        class_ids = [classroom.id for classroom in classroom_options]
        counts = self.repository.get_enrollment_counts(class_ids, now)
        sessions = self.repository.get_first_sessions(class_ids, completed_through or 0, now)
        return PermanentTransferOptionsResponse(
            current_class=_transfer_class(current_class),
            current_enrollment_id=current.id,
            completed_through_teaching_week=completed_through,
            options=[
                PermanentTransferOption(
                    class_id=classroom.id,
                    class_name=classroom.name,
                    is_full=counts.get(classroom.id, 0) >= classroom.default_capacity,
                    first_session=_first_session(sessions.get(classroom.id)),
                )
                for classroom in classroom_options
            ],
        )

    def confirm_transfer(
        self, student_id: int, request: ConfirmPermanentTransferRequest
    ) -> ConfirmPermanentTransferResponse:
        with self.repository.transaction():
            grade = self.schedule_repository.lock_student_grade(student_id)
            if grade is None:
                raise StudentGradeNotFoundException()

            current = self.repository.lock_current_enrollment(
                student_id, request.expected_current_enrollment_id, clock.center_local_now()
            )
            if current is None:
                raise PermanentTransferConflict(PermanentTransferConflictDetail(code="SOURCE_CHANGED"))

            locked_classes = self.repository.lock_classes([current.class_id, request.target_class_id])
            now = clock.center_local_now().replace(microsecond=0)
            target = locked_classes.get(request.target_class_id)
            if (
                target is None
                or target.id == current.class_id
                or target.grade != grade
            ):
                raise PermanentTransferConflict(PermanentTransferConflictDetail(code="TARGET_UNAVAILABLE"))

            completed_through = self.schedule_repository.get_completed_through_week(student_id, grade) or 0
            while True:
                candidate = self.repository.lock_first_session(target.id, completed_through, now)
                now = clock.center_local_now().replace(microsecond=0)
                if candidate is None or candidate.ends_at > now:
                    break
            if target.ends_at is not None and target.ends_at <= now:
                raise PermanentTransferConflict(PermanentTransferConflictDetail(code="TARGET_UNAVAILABLE"))
            if current.ends_at is not None and current.ends_at <= now:
                raise PermanentTransferConflict(PermanentTransferConflictDetail(code="SOURCE_CHANGED"))

            # Count after locking the class so competing transfers cannot claim the same seat.
            counts = self.repository.get_enrollment_counts([target.id], now)
            if counts.get(target.id, 0) >= target.default_capacity:
                raise PermanentTransferConflict(PermanentTransferConflictDetail(code="CLASS_FULL"))

            first = _first_session(candidate)
            snapshot = FirstSessionSnapshot(**first.model_dump(exclude={"topic"})) if first else None
            if request.expected_first_session != snapshot:
                raise PermanentTransferConflict(
                    PermanentTransferConflictDetail(code="FIRST_SESSION_CHANGED", first_session=first)
                )

            self.repository.supersede_unfinished_temporary_transfers(student_id, now)
            enrollment = self.repository.replace_enrollment(
                current=current,
                target_class_id=target.id,
                now=now,
                completed_through=completed_through,
                entry_session_id=first.session_id if first else None,
            )
            return ConfirmPermanentTransferResponse(
                new_class=_transfer_class(target),
                enrollment_id=enrollment.id,
                transferred_at=now,
                first_session=first,
            )
