from sqlalchemy.exc import IntegrityError

from app.core import clock
from app.models.exam import Exam
from app.modules.exams.exam_bank.repository import ExamBankRepository
from .exceptions import DraftConflictError, DraftGoneError, DraftNotFoundError

from .repository import ExamDraftRepository
from .schemas import CreateExamDraftRequest, ExamDraftResponse, UpdateExamDraftRequest


class ExamDraftService:
    def __init__(self, repository: ExamDraftRepository, exam_bank: ExamBankRepository) -> None:
        self.repository = repository
        self.exam_bank = exam_bank

    def create_draft(self, teacher_id: int, request: CreateExamDraftRequest) -> int:
        key = str(request.autosave_key) if request.autosave_key is not None else None
        try:
            with self.repository.transaction():
                if key is not None:
                    existing = self.repository.get_by_autosave_key(teacher_id, key)
                    if existing is not None:
                        return self._active_autosave_id(existing)
                self._require_usable_paper(teacher_id, request.paper_id)
                exam = Exam(
                    **request.model_dump(exclude={"autosave_key"}),
                    created_by=teacher_id,
                    status="draft",
                    created_at=clock.center_local_now(),
                    autosave_key=key,
                )
                return self.repository.add(exam)
        except IntegrityError:
            # Hai lần gửi cùng khóa có thể cùng thấy chưa có bản nháp trước INSERT.
            if key is not None:
                existing = self.repository.get_by_autosave_key(teacher_id, key)
                if existing is not None:
                    return self._active_autosave_id(existing)
            raise

    def list_drafts(self, teacher_id: int) -> list[ExamDraftResponse]:
        return [ExamDraftResponse.model_validate(exam) for exam in self.repository.list_drafts(teacher_id)]

    def get_draft(self, teacher_id: int, exam_id: int) -> ExamDraftResponse:
        return ExamDraftResponse.model_validate(self._get_draft(teacher_id, exam_id))

    def get_draft_by_autosave_key(self, teacher_id: int, key: str) -> ExamDraftResponse:
        exam = self.repository.get_by_autosave_key(teacher_id, key)
        if exam is None:
            raise DraftNotFoundError("Không tìm thấy kỳ thi nháp.")
        self._active_autosave_id(exam)
        return ExamDraftResponse.model_validate(exam)

    def update_draft(self, teacher_id: int, exam_id: int, request: UpdateExamDraftRequest) -> ExamDraftResponse:
        with self.repository.transaction():
            exam = self._get_draft(teacher_id, exam_id, for_update=True)
            if exam.version != request.version:
                raise DraftConflictError("Bản nháp đã được cập nhật ở nơi khác.")
            self._require_usable_paper(teacher_id, request.paper_id)
            for field, value in request.model_dump(exclude={"version"}).items():
                setattr(exam, field, value)
            exam.version += 1
            return ExamDraftResponse.model_validate(exam)

    def delete_draft(self, teacher_id: int, exam_id: int) -> None:
        with self.repository.transaction():
            exam = self._get_draft(teacher_id, exam_id, for_update=True)
            # Giữ lại khóa tự lưu để POST bị gửi lại không dựng lại bản đã xóa.
            exam.discarded_at = clock.center_local_now()
            exam.paper_id = exam.title = exam.description = None
            exam.opens_at = exam.closes_at = exam.duration_minutes = None
            exam.schedule_inputs = None

    def _get_draft(self, teacher_id: int, exam_id: int, *, for_update: bool = False) -> Exam:
        exam = self.repository.get_draft(teacher_id, exam_id, for_update=for_update)
        if exam is None:
            raise DraftNotFoundError("Không tìm thấy kỳ thi nháp.")
        if exam.discarded_at is not None:
            raise DraftGoneError("Bản nháp đã được xóa.")
        return exam

    def _require_usable_paper(self, teacher_id: int, paper_id: int | None) -> None:
        if paper_id is not None and self.exam_bank.get_owned_paper_id(paper_id, teacher_id) is None:
            raise DraftNotFoundError("Không tìm thấy đề thi có thể sử dụng trong Kho đề.")

    @staticmethod
    def _active_autosave_id(exam: Exam) -> int:
        if exam.discarded_at is not None or exam.status != "draft":
            raise DraftGoneError("Bản nháp này đã được xử lý.")
        return exam.id
