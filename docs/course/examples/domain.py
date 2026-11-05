"""Lời giải học tập: nghiệp vụ thuần, không có HTTP, MySQL hay xác thực JWT.

Actor/now do bên gọi đáng tin cung cấp. Memory repository không mô phỏng khóa,
transaction hoặc đảm bảo cạnh tranh của MySQL. Không nối trực tiếp vào production.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import re
from typing import Protocol


class Role(Enum):
    STUDENT = 'student'
    TEACHER = 'teacher'
    ASSISTANT = 'teaching_assistant'
    ADMIN = 'admin'


class AssignmentStatus(Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    CLOSED = 'closed'


class DomainError(Exception):
    pass


class AccessDenied(DomainError):
    pass


class AssignmentNotFound(DomainError):
    pass


class InvalidAnswer(DomainError):
    pass


class AssignmentUnavailable(DomainError):
    pass


class DeadlinePassed(DomainError):
    pass


class AlreadySubmitted(DomainError):
    pass


def require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('Thời điểm phải có timezone')


@dataclass(frozen=True)
class Actor:
    user_id: int
    role: Role
    active: bool = True


@dataclass(frozen=True)
class Assignment:
    id: int
    class_id: int
    status: AssignmentStatus
    due_at: datetime | None

    def __post_init__(self) -> None:
        if self.due_at is not None:
            require_aware(self.due_at)


@dataclass(frozen=True)
class Submission:
    id: int
    assignment_id: int
    student_id: int
    answer: str
    submitted_at: datetime


class SubmissionRepository(Protocol):
    def find_assignment(self, assignment_id: int) -> Assignment | None: ...

    def is_member(self, class_id: int, user_id: int) -> bool: ...

    def find_submission(self, assignment_id: int, student_id: int) -> Submission | None: ...

    def create_submission(
        self, assignment_id: int, student_id: int, answer: str, submitted_at: datetime,
    ) -> Submission: ...


class MemorySubmissionRepository:
    """Fake riêng cho mỗi bài/test; không dùng chung object giữa các test."""

    def __init__(self) -> None:
        self.assignments: dict[int, Assignment] = {}
        self.memberships: set[tuple[int, int]] = set()
        self.submissions: dict[tuple[int, int], Submission] = {}
        self._next_id = 1

    def find_assignment(self, assignment_id: int) -> Assignment | None:
        return self.assignments.get(assignment_id)

    def is_member(self, class_id: int, user_id: int) -> bool:
        return (class_id, user_id) in self.memberships

    def find_submission(self, assignment_id: int, student_id: int) -> Submission | None:
        return self.submissions.get((assignment_id, student_id))

    def create_submission(
        self, assignment_id: int, student_id: int, answer: str, submitted_at: datetime,
    ) -> Submission:
        key = (assignment_id, student_id)
        if key in self.submissions:
            raise AlreadySubmitted('Đã có bài nộp')
        submission = Submission(
            id=self._next_id,
            assignment_id=assignment_id,
            student_id=student_id,
            answer=answer,
            submitted_at=submitted_at,
        )
        self.submissions[key] = submission
        self._next_id += 1
        return submission


class SubmitService:
    def __init__(self, repository: SubmissionRepository) -> None:
        self.repository = repository

    def submit(
        self, actor: Actor, assignment_id: int, answer: str, now: datetime,
    ) -> Submission:
        require_aware(now)
        if not actor.active or actor.role is not Role.STUDENT:
            raise AccessDenied('Chỉ học sinh đang hoạt động được nộp')
        assignment = self.repository.find_assignment(assignment_id)
        if assignment is None:
            raise AssignmentNotFound('Không tìm thấy bài tập')
        if not self.repository.is_member(assignment.class_id, actor.user_id):
            raise AccessDenied('Không thuộc lớp của bài tập')
        normalized = answer.strip()
        if not 1 <= len(normalized) <= 10_000:
            raise InvalidAnswer('Nội dung cần từ 1 đến 10000 ký tự sau khi trim')
        existing = self.repository.find_submission(assignment_id, actor.user_id)
        if existing is not None:
            if existing.answer == normalized:
                return existing
            raise AlreadySubmitted('Phiên bản này chưa hỗ trợ sửa bài đã nộp')
        if assignment.status is not AssignmentStatus.PUBLISHED:
            raise AssignmentUnavailable('Bài chưa công bố hoặc đã đóng')
        if assignment.due_at is not None and now > assignment.due_at:
            raise DeadlinePassed('Đã quá hạn nộp')
        return self.repository.create_submission(
            assignment_id, actor.user_id, normalized, now,
        )


def validate_score(score: Decimal) -> Decimal:
    """Thang 0–10 là quy tắc bài học; không tự chuyển float thành Decimal."""
    if not isinstance(score, Decimal):
        raise TypeError('Dùng Decimal tạo từ chuỗi')
    if not score.is_finite() or score < 0 or score > 10:
        raise ValueError('Điểm phải hữu hạn và trong khoảng 0–10')
    return score


def parse_decimal_answer(text: str) -> Decimal:
    normalized = text.strip()
    if len(normalized) > 100 or re.fullmatch(r'[+-]?[0-9]+(?:\.[0-9]+)?', normalized) is None:
        raise ValueError('Định dạng số không hợp lệ')
    return Decimal(normalized)


def grade_numeric(expected: str, answer: str) -> int:
    """Chỉ so sánh số thập phân chính xác theo hợp đồng hẹp của chương 11."""
    return int(parse_decimal_answer(expected) == parse_decimal_answer(answer))
