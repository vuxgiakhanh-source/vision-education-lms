"""Lỗi nghiệp vụ của phòng thi. Mỗi lỗi có `code` ổn định để router đổi thành mã HTTP."""

from __future__ import annotations


class ExamDomainError(Exception):
    code = "exam_error"

    def __init__(self, message: str = "") -> None:
        super().__init__(message or self.code)


class NotAllowedToEnter(ExamDomainError):
    code = "not_allowed_to_enter"  # 403: không có tên, kỳ thi chưa mở/đã đóng/chưa phát hành


class AttemptClosed(ExamDomainError):
    code = "attempt_closed"  # 410: đã nộp hoặc quá hạn

    def __init__(self, message: str = "", receipt_code: str | None = None) -> None:
        super().__init__(message)
        self.receipt_code = receipt_code  # có khi lượt đã nộp: trả lại để em thấy bài mình đã được ghi


class EpochMismatch(ExamDomainError):
    code = "epoch_mismatch"  # 409: thiết bị khác đang giữ quyền ghi


class VersionConflict(ExamDomainError):
    code = "version_conflict"  # 409: bản lưu của máy chủ đã khác bản máy đang giữ

    def __init__(self, server_answers: dict, server_version: int) -> None:
        super().__init__("Bản lưu trên máy chủ đã khác.")
        self.server_answers = server_answers
        self.server_version = server_version


class RequestIdReused(ExamDomainError):
    code = "request_id_reused"  # 409: cùng request_id nhưng nội dung khác


class InvalidTeacherAction(ExamDomainError):
    code = "invalid_teacher_action"  # 409/422: thao tác của giáo viên không hợp lệ ở trạng thái hiện tại


class AnswerKeyIncomplete(ExamDomainError):
    code = "answer_key_incomplete"  # 422: thiếu đáp án, kèm vị trí

    def __init__(self, missing: list[str]) -> None:
        super().__init__("Thiếu đáp án: " + ", ".join(missing))
        self.missing = missing
