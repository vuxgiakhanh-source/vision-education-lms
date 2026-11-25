"""Điều phối lượt thi: bắt đầu, lưu, nộp, quét chốt, chuyển quyền ghi.

Quy tắc (docs/design/exam-room-concurrency.md):
- Máy chủ quyết định đúng/sai: hạn nộp, quyền ghi, trạng thái lượt đều kiểm trong chính câu lệnh ghi.
- Mọi thao tác ghi lặp lại được: gửi lại cùng yêu cầu cho ra cùng kết quả.
- Đường nộp tay và đường quét tự động dùng CÙNG MỘT hàm chốt để chỉ có một nguồn quy tắc.
- Không bao giờ mất đáp án: chấm lỗi thì lượt vẫn ở trạng thái đang làm với đáp án đã lưu, để thử lại.
"""

from __future__ import annotations

import json
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.exc import IntegrityError

from app.core.clock import center_local_now
from app.modules.exams.attempts.repository import AttemptRepository
from app.modules.exams.domain.deadline import (
    DEFAULT_GRACE_SECONDS,
    can_enter,
    compute_deadline,
    grace_floor,
    is_within_grace,
)
from app.modules.exams.domain.errors import (
    AttemptClosed,
    EpochMismatch,
    NotAllowedToEnter,
    RequestIdReused,
    VersionConflict,
)
from app.modules.exams.domain.grading import DEFAULT_SCORING, grade
from app.modules.exams.domain.monitor import (
    ALLOWED_EVENT_TYPES,
    MAX_EVENT_PAYLOAD_BYTES,
    MAX_EVENTS_PER_ATTEMPT,
    MAX_EVENTS_PER_REQUEST,
)
from app.modules.exams.domain.receipt import content_digest, new_receipt_code

# Máy khác đang ghi và còn "sống" trong khoảng này thì không tự chiếm quyền, phải để em xác nhận.
TAKEOVER_IDLE_SECONDS = 60
RECEIPT_RETRIES = 5


@dataclass
class AttemptView:
    id: int
    deadline_at: datetime
    status: str
    answers: dict[str, Any]
    answers_version: int
    write_epoch: int
    device_id: str | None
    shuffle_seed: int | None
    receipt_code: str | None
    takeover_required: bool = False


@dataclass
class SubmitResult:
    attempt_id: int
    status: str
    receipt_code: str
    submitted_at: datetime
    content_digest: str
    score: Any
    max_score: Any
    late: bool = False
    replayed: bool = False


@dataclass
class Progress:
    """Số liệu cho cô theo dõi, do trình duyệt báo. Chỉ để cân nhắc, không dùng để trừ điểm."""

    current_item: str | None = None
    item_ms: dict[str, int] | None = None
    away_count: int = 0
    away_ms: int = 0
    fullscreen_exit_count: int = 0
    offline_count: int = 0


class AttemptService:
    def __init__(
        self,
        repo: AttemptRepository,
        now_fn: Callable[[], datetime] = center_local_now,
        grace_seconds: int = DEFAULT_GRACE_SECONDS,
    ) -> None:
        self.repo = repo
        self.db = repo.db
        self.now_fn = now_fn
        self.grace_seconds = grace_seconds

    # ----- bắt đầu hoặc tiếp tục -----
    def start(self, exam_id: int, student_id: int, device_id: str | None = None) -> AttemptView:
        now = self.now_fn()
        exam = self.repo.get_exam_for_participant(exam_id, student_id)
        if exam is None or exam.status != "published":
            raise NotAllowedToEnter("Không có tên trong kỳ thi hoặc kỳ thi chưa mở.")

        attempt = self.repo.get_current_attempt(exam_id, student_id)
        if attempt is None:
            if not can_enter(now, exam.opens_at, exam.closes_at):
                raise NotAllowedToEnter("Ngoài khung giờ vào phòng thi.")
            self.repo.create_first_attempt_if_absent(
                exam_id=exam_id, student_id=student_id, now=now,
                deadline_at=compute_deadline(now, exam.closes_at, exam.duration_minutes),
                device_id=device_id, shuffle_seed=secrets.randbits(62),
            )
            self.db.commit()
            attempt = self.repo.get_current_attempt(exam_id, student_id)
        # Xét đổi máy bằng last_seen_at CŨ, trước khi làm mới. Máy lạ không được làm mới dấu hiệu "còn sống"
        # của máy đang giữ quyền, nếu không máy thứ hai nào cũng thấy máy đầu vừa hoạt động.
        other_device = bool(device_id) and bool(attempt.device_id) and attempt.device_id != device_id
        takeover = (
            attempt.status == "in_progress"
            and other_device
            and attempt.last_seen_at is not None
            and now - attempt.last_seen_at < timedelta(seconds=TAKEOVER_IDLE_SECONDS)
        )
        if not other_device and attempt.status == "in_progress":
            self.repo.touch(attempt.id, now)
            self.db.commit()
            self.db.refresh(attempt)
        return self._view(attempt, takeover_required=takeover)

    def take_over(self, attempt_id: int, student_id: int, device_id: str) -> AttemptView:
        """Em xác nhận chuyển sang máy này. Máy cũ gửi epoch cũ sẽ bị từ chối."""
        updated = self.repo.take_over_write(
            attempt_id=attempt_id, student_id=student_id, device_id=device_id, now=self.now_fn()
        )
        self.db.commit()
        if updated != 1:
            raise AttemptClosed("Lượt thi không còn đang làm.")
        attempt = self.repo.get_attempt(attempt_id)
        return self._view(attempt)

    # ----- lưu bài -----
    def sync(
        self, attempt_id: int, student_id: int, *, epoch: int, base_version: int,
        answers: dict[str, Any], progress: Progress | None = None,
    ) -> int:
        """Lưu toàn bộ đáp án. Trả answers_version mới. Ném lỗi nghiệp vụ nếu không ghi được."""
        now = self.now_fn()
        p = progress or Progress()
        matched = self.repo.save_answers(
            attempt_id=attempt_id, student_id=student_id, epoch=epoch, base_version=base_version,
            answers=answers, now=now, grace_floor=grace_floor(now, self.grace_seconds),
            current_item=p.current_item, item_ms=p.item_ms, away_count=p.away_count,
            away_ms=p.away_ms, fullscreen_exit_count=p.fullscreen_exit_count,
            offline_count=p.offline_count,
        )
        if matched == 1:
            self.db.commit()
            return base_version + 1
        self.db.rollback()
        return self._explain_failed_save(attempt_id, student_id, epoch, base_version, answers, now)

    def _explain_failed_save(
        self, attempt_id: int, student_id: int, epoch: int, base_version: int,
        answers: dict[str, Any], now: datetime,
    ) -> int:
        """Một truy vấn chẩn đoán (đường hiếm) để chọn đúng lỗi. Trả version nếu thực ra đã lưu thành công."""
        attempt = self.repo.get_attempt(attempt_id)
        if attempt is None or attempt.student_id != student_id:
            raise NotAllowedToEnter("Không tìm thấy lượt thi.")
        if not self.repo.is_student_active(student_id):
            raise NotAllowedToEnter("Tài khoản đã bị khóa.")
        if attempt.status != "in_progress":
            raise AttemptClosed("Bài đã nộp.", receipt_code=attempt.receipt_code)
        if not is_within_grace(now, attempt.deadline_at, self.grace_seconds):
            raise AttemptClosed("Đã quá hạn nộp.")
        if attempt.write_epoch != epoch:
            raise EpochMismatch("Thiết bị khác đang giữ quyền ghi.")
        if attempt.answers_version != base_version:
            # Phản hồi lần lưu trước bị mất, máy gửi lại đúng nội dung: coi như đã thành công.
            if attempt.answers_version == base_version + 1 and attempt.answers == answers:
                return attempt.answers_version
            raise VersionConflict(attempt.answers, attempt.answers_version)
        raise RuntimeError("Lưu bài thất bại mà không tìm ra lý do.")

    # ----- nộp bài -----
    def submit(
        self, attempt_id: int, student_id: int, *, epoch: int, answers: dict[str, Any], request_id: str
    ) -> SubmitResult:
        now = self.now_fn()
        attempt = self.repo.lock_attempt(attempt_id, student_id)  # mở giao dịch, khóa dòng của chính em
        if attempt is None:
            self.db.rollback()
            raise NotAllowedToEnter("Không tìm thấy lượt thi.")
        digest = content_digest(answers)

        if attempt.status != "in_progress":
            try:
                return self._replay(attempt, request_id, digest)
            finally:
                self.db.rollback()

        if attempt.write_epoch != epoch:
            self.db.rollback()
            raise EpochMismatch("Thiết bị khác đang giữ quyền ghi.")

        late = not is_within_grace(now, attempt.deadline_at, self.grace_seconds)
        if late:
            # Bài chính thức là bản đã đồng bộ gần nhất; phần đến muộn lưu riêng cho cô quyết định.
            self.repo.add_late_submission(
                attempt_id=attempt.id, answers=answers, now=now, reason="submitted_after_grace"
            )
            final_answers, status = dict(attempt.answers or {}), "auto_submitted"
        else:
            final_answers, status = answers, "submitted"
        try:
            result = self._grade_and_finalize(
                attempt, final_answers, status, request_id, now, reason="submit"
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        result.late = late
        return result

    def _replay(self, attempt: Any, request_id: str, digest: str) -> SubmitResult:
        """Lượt đã nộp: cùng request_id và cùng nội dung thì trả lại đúng biên nhận (gửi lặp vô hại)."""
        if attempt.submit_request_id == request_id:
            if attempt.content_digest != digest:
                raise RequestIdReused("Cùng mã yêu cầu nhưng nội dung khác.")
            return SubmitResult(
                attempt_id=attempt.id, status=attempt.status, receipt_code=attempt.receipt_code,
                submitted_at=attempt.submitted_at, content_digest=attempt.content_digest,
                score=attempt.score, max_score=attempt.max_score, replayed=True,
            )
        raise AttemptClosed("Bài đã được nộp trước đó.", receipt_code=attempt.receipt_code)

    def _grade_and_finalize(
        self, attempt: Any, final_answers: dict[str, Any], status: str,
        request_id: str | None, now: datetime, *, reason: str,
    ) -> SubmitResult:
        """MỘT hàm chốt cho cả nộp tay và quét tự động. Gọi trong giao dịch đã khóa dòng lượt thi."""
        paper_id = self.repo.get_paper_id_for_attempt(attempt.exam_id)
        key_row = self.repo.get_answer_key(paper_id) if paper_id else None
        if key_row is None:
            # Kỳ thi đã phát hành thì phải có khóa. Thiếu thì dừng, lượt giữ nguyên để thử lại, không mất bài.
            raise RuntimeError(f"Thiếu khóa đáp án cho đề {paper_id}.")
        scoring = key_row.scoring or DEFAULT_SCORING
        result = grade(key_row.key, scoring, final_answers)
        digest = content_digest(final_answers)

        for attempt_no in range(RECEIPT_RETRIES):
            code = new_receipt_code()
            try:
                with self.db.begin_nested():  # điểm lưu: trùng mã biên nhận thì thử mã khác, không bỏ cả giao dịch
                    self.repo.finalize(
                        attempt_id=attempt.id, status=status, answers=final_answers, now=now,
                        request_id=request_id, receipt_code=code, digest=digest,
                        score=result.score, max_score=result.max_score,
                    )
                break
            except IntegrityError:
                if attempt_no == RECEIPT_RETRIES - 1:
                    raise
        self.repo.add_grade_history(
            attempt_id=attempt.id, key_version=key_row.version, score=result.score, now=now, reason=reason
        )
        return SubmitResult(
            attempt_id=attempt.id, status=status, receipt_code=code, submitted_at=now,
            content_digest=digest, score=result.score, max_score=result.max_score,
        )

    # ----- quét chốt các lượt quá hạn -----
    def sweep(self, batch_size: int = 100) -> int:
        """Chốt mọi lượt quá hạn bằng bản đáp án đã đồng bộ. Trả số lượt đã chốt. Chạy lặp lại vô hại."""
        finalized = 0
        while True:
            now = self.now_fn()
            ids = self.repo.lock_expired_attempt_ids(
                cutoff=now - timedelta(seconds=self.grace_seconds), limit=batch_size
            )
            if not ids:
                self.db.rollback()
                return finalized
            done_in_batch = 0
            try:
                for attempt_id in ids:
                    attempt = self.repo.get_attempt(attempt_id)
                    if attempt is None or attempt.status != "in_progress":
                        continue
                    self._grade_and_finalize(
                        attempt, dict(attempt.answers or {}), "auto_submitted", None, now,
                        reason="auto_submit",
                    )
                    done_in_batch += 1
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            finalized += done_in_batch
            if len(ids) < batch_size:
                return finalized

    # ----- trợ giúp -----
    @staticmethod
    def _view(attempt: Any, takeover_required: bool = False) -> AttemptView:
        return AttemptView(
            id=attempt.id, deadline_at=attempt.deadline_at, status=attempt.status,
            answers=dict(attempt.answers or {}), answers_version=attempt.answers_version,
            write_epoch=attempt.write_epoch, device_id=attempt.device_id,
            shuffle_seed=attempt.shuffle_seed, receipt_code=attempt.receipt_code,
            takeover_required=takeover_required,
        )

    # ----- chốt theo yêu cầu của giáo viên -----
    def force_submit(self, attempt_id: int, *, reason: str = "teacher_force") -> SubmitResult:
        """Buộc nộp một lượt bằng bản đáp án đã đồng bộ. Dùng CÙNG hàm chốt với nộp tay và quét tự động."""
        now = self.now_fn()
        attempt = self.repo.lock_attempt(attempt_id)
        if attempt is None:
            self.db.rollback()
            raise NotAllowedToEnter("Không tìm thấy lượt thi.")
        if attempt.status != "in_progress":
            receipt = attempt.receipt_code
            self.db.rollback()
            raise AttemptClosed("Lượt thi đã được nộp.", receipt_code=receipt)
        try:
            result = self._grade_and_finalize(
                attempt, dict(attempt.answers or {}), "auto_submitted", None, now, reason=reason
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return result

    # ----- sự kiện do trình duyệt báo -----
    def record_events(self, attempt_id: int, student_id: int, events: list[dict[str, Any]]) -> int:
        """Ghi nhật ký sự kiện (rời màn hình, thoát toàn màn hình, mất mạng...). Trả số sự kiện đã ghi.

        Gửi lại cùng lô vô hại: sự kiện có client_seq đã ghi bị bỏ qua. Loại sự kiện nằm trong danh sách đóng,
        mỗi lô tối đa MAX_EVENTS_PER_REQUEST sự kiện và mỗi lượt tối đa MAX_EVENTS_PER_ATTEMPT để không ai nhét đầy bảng.
        """
        now = self.now_fn()
        attempt = self.repo.get_attempt(attempt_id)
        if attempt is None or attempt.student_id != student_id:
            self.db.rollback()
            raise NotAllowedToEnter("Không tìm thấy lượt thi.")
        room = MAX_EVENTS_PER_ATTEMPT - self.repo.count_events(attempt_id)
        last_seq = self.repo.max_client_seq(attempt_id)
        written = 0
        for event in events[:MAX_EVENTS_PER_REQUEST]:
            if written >= room:
                break
            kind = event.get("type")
            payload = event.get("payload")
            if kind not in ALLOWED_EVENT_TYPES:
                continue
            if payload is not None and len(json.dumps(payload, ensure_ascii=False)) > MAX_EVENT_PAYLOAD_BYTES:
                continue
            seq = event.get("seq")
            if isinstance(seq, int):
                if seq <= last_seq:
                    continue
                last_seq = seq
            else:
                seq = None
            offset = event.get("offset_ms")
            self.repo.add_event(
                attempt_id=attempt_id, type=kind, now=now, client_seq=seq,
                client_offset_ms=offset if isinstance(offset, int) else None, payload=payload,
            )
            written += 1
        self.db.commit()
        return written
