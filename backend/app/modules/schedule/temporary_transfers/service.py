from .. import service as schedule_service
from ..exceptions import StudentGradeNotFoundException
from ..repository import ScheduleRepository
from .repository import TemporaryTransferRepository
from .schemas import (
    ConfirmTemporaryTransferRequest,
    ConfirmTemporaryTransferResponse,
    TemporaryTransferConflictDetail,
    TemporaryTransferOption,
    TemporaryTransferOptionsResponse,
    TemporaryTransferSource,
)


class TemporaryTransferConflict(Exception):
    def __init__(self, detail: TemporaryTransferConflictDetail):
        super().__init__(detail.code)
        self.detail = detail


class TemporaryTransferService:
    def __init__(
        self,
        repository: TemporaryTransferRepository,
        schedule_repository: ScheduleRepository,
    ):
        self.repository = repository
        self.schedule_repository = schedule_repository

    def get_options(self, student_id: int) -> TemporaryTransferOptionsResponse:
        grade = self.schedule_repository.get_student_grade(student_id)
        if grade is None:
            raise StudentGradeNotFoundException()

        now = schedule_service.schedule_now()
        assignment = self.schedule_repository.get_first_unfinished_assignment(
            student_id=student_id, grade=grade, now=now
        )
        if assignment is None:
            return TemporaryTransferOptionsResponse(
                source=None, options=[], blocked_reason="NO_UPCOMING_SESSION"
            )

        original, current, enrollment_id = assignment
        source = TemporaryTransferSource(
            enrollment_id=enrollment_id,
            original_session_id=original.id,
            current_session_id=current.id,
            teaching_week=original.teaching_week,
            topic=current.topic,
            starts_at=current.starts_at,
            ends_at=current.ends_at,
        )
        if original.teaching_week is None:
            return TemporaryTransferOptionsResponse(
                source=source, options=[], blocked_reason="MISSING_TEACHING_WEEK"
            )

        sessions = self.repository.list_replacement_sessions(
            grade=grade,
            teaching_week=original.teaching_week,
            now=now,
            excluded_session_ids=[current.id],
        )
        options = [
            TemporaryTransferOption(
                session_id=session.id, starts_at=session.starts_at, ends_at=session.ends_at
            )
            for session in sessions
        ]
        return TemporaryTransferOptionsResponse(
            source=source,
            options=options,
            blocked_reason=None if options else "NO_ELIGIBLE_SESSIONS",
        )

    def confirm_transfer(
        self, student_id: int, original_session_id: int, request: ConfirmTemporaryTransferRequest
    ) -> ConfirmTemporaryTransferResponse:
        with self.repository.transaction():
            grade = self.schedule_repository.lock_student_grade(student_id)
            if grade is None:
                raise StudentGradeNotFoundException()

            current_session_id = request.expected_current_session_id
            self.repository.lock_sessions(
                [original_session_id, current_session_id, request.target_session_id]
            )
            now = schedule_service.schedule_now()

            if self.schedule_repository.has_student_attended(student_id, current_session_id):
                raise TemporaryTransferConflict(TemporaryTransferConflictDetail(code="ALREADY_PRESENT"))

            assignment = self.schedule_repository.get_first_unfinished_assignment(
                student_id=student_id, grade=grade, now=now
            )
            if (
                assignment is None
                or assignment.enrollment_id != request.expected_enrollment_id
                or assignment.original.id != original_session_id
                or assignment.current.id != current_session_id
            ):
                raise TemporaryTransferConflict(TemporaryTransferConflictDetail(code="SOURCE_CHANGED"))

            original, current, _ = assignment
            if original.teaching_week is None or request.target_session_id == current.id:
                raise TemporaryTransferConflict(TemporaryTransferConflictDetail(code="TARGET_UNAVAILABLE"))

            target = self.repository.get_replacement_session(
                session_id=request.target_session_id,
                grade=grade,
                teaching_week=original.teaching_week,
                now=now,
            )
            if target is None:
                raise TemporaryTransferConflict(TemporaryTransferConflictDetail(code="TARGET_UNAVAILABLE"))
            if (
                target.starts_at != request.expected_target_starts_at
                or target.ends_at != request.expected_target_ends_at
            ):
                raise TemporaryTransferConflict(
                    TemporaryTransferConflictDetail(
                        code="SESSION_TIME_CHANGED",
                        option=TemporaryTransferOption(
                            session_id=target.id, starts_at=target.starts_at, ends_at=target.ends_at
                        ),
                    )
                )

            replacement_id = None if target.id == original.id else target.id
            self.repository.set_replacement(student_id, original.id, replacement_id)
            return ConfirmTemporaryTransferResponse(
                original_session_id=original.id, current_session_id=target.id
            )
