"""Theo dõi và điều khiển phòng thi của giáo viên.

Nguyên tắc:
- Mọi thao tác lên bài của em đều bắt buộc có lý do và được ghi nhật ký (ai, lúc nào, làm gì) trong bảng sự kiện.
- Giáo viên không sửa được đáp án của em, cũng không sửa đề trong giờ thi: chỉ gia hạn, buộc nộp, mở lại, mở lượt mới.
- Buộc nộp dùng CÙNG hàm chốt với nộp tay và quét tự động.
- Số liệu rời màn hình, thoát toàn màn hình, offline do trình duyệt báo: chỉ để cân nhắc, không tự trừ điểm.
"""

from __future__ import annotations

import secrets
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.clock import center_local_now
from app.models.exam import ExamAttempt, ExamParticipant
from app.modules.exams.attempts.repository import AttemptRepository
from app.modules.exams.attempts.service import AttemptService, SubmitResult
from app.modules.exams.domain.errors import InvalidTeacherAction, NotAllowedToEnter
from app.modules.exams.domain.monitor import classify
from app.modules.exams.monitor.repository import MonitorRepository

MAX_EXTENSION_MINUTES = 240


@dataclass
class StudentStatus:
    student_id: int
    full_name: str
    state: str
    attempt_id: int | None
    attempt_no: int | None
    answered: int
    current_item: str | None
    started_at: datetime | None
    deadline_at: datetime | None
    last_seen_at: datetime | None
    seconds_since_seen: int | None
    submitted_at: datetime | None
    score: Any
    max_score: Any
    away_count: int
    away_ms: int
    fullscreen_exit_count: int
    offline_count: int
    extra_attempt_reason: str | None


@dataclass
class ExamOverview:
    students: list[StudentStatus]
    totals: dict[str, int]


class MonitorService:
    def __init__(self, repo: MonitorRepository, now_fn: Callable[[], datetime] = center_local_now) -> None:
        self.repo = repo
        self.now_fn = now_fn

    def overview(self, exam_id: int) -> ExamOverview:
        now = self.now_fn()
        students: list[StudentStatus] = []
        for row in self.repo.list_participants_with_latest_attempt(exam_id):
            state = classify(status=row.status, last_seen_at=row.last_seen_at, now=now)
            seen = int((now - row.last_seen_at).total_seconds()) if row.last_seen_at else None
            students.append(
                StudentStatus(
                    student_id=row.student_id, full_name=row.full_name, state=state, attempt_id=row.attempt_id,
                    attempt_no=row.attempt_no, answered=int(row.answered or 0), current_item=row.current_item,
                    started_at=row.started_at, deadline_at=row.deadline_at, last_seen_at=row.last_seen_at,
                    seconds_since_seen=seen, submitted_at=row.submitted_at, score=row.score, max_score=row.max_score,
                    away_count=row.away_count or 0, away_ms=row.away_ms or 0,
                    fullscreen_exit_count=row.fullscreen_exit_count or 0, offline_count=row.offline_count or 0,
                    extra_attempt_reason=row.grant_reason,
                )
            )
        totals = dict(Counter(s.state for s in students))
        totals["total"] = len(students)
        return ExamOverview(students=students, totals=totals)


class TeacherControlService:
    def __init__(self, attempts: AttemptService, now_fn: Callable[[], datetime] | None = None) -> None:
        self.attempts = attempts
        self.repo: AttemptRepository = attempts.repo
        self.db = attempts.db
        self.now_fn = now_fn or attempts.now_fn

    # ----- quy tắc chung -----
    @staticmethod
    def _need_reason(reason: str) -> str:
        reason = (reason or "").strip()
        if not reason:
            raise InvalidTeacherAction("Phải ghi lý do cho thao tác này.")
        return reason

    @staticmethod
    def _need_minutes(minutes: int) -> int:
        if not isinstance(minutes, int) or isinstance(minutes, bool) or not 1 <= minutes <= MAX_EXTENSION_MINUTES:
            raise InvalidTeacherAction(f"Số phút phải từ 1 đến {MAX_EXTENSION_MINUTES}.")
        return minutes

    def _log(self, attempt_id: int, kind: str, teacher_id: int, reason: str, **extra: Any) -> None:
        self.repo.add_event(
            attempt_id=attempt_id, type=kind, now=self.now_fn(),
            payload={"teacher_id": teacher_id, "reason": reason, **extra},
        )

    # ----- gia hạn -----
    def extend_attempt(self, attempt_id: int, *, minutes: int, teacher_id: int, reason: str) -> datetime:
        """Gia hạn một em. Trả hạn nộp mới."""
        reason, minutes = self._need_reason(reason), self._need_minutes(minutes)
        attempt = self.repo.lock_attempt(attempt_id)
        if attempt is None:
            self.db.rollback()
            raise NotAllowedToEnter("Không tìm thấy lượt thi.")
        if attempt.status != "in_progress":
            self.db.rollback()
            raise InvalidTeacherAction('Lượt thi đã nộp; dùng "mở lại" hoặc "mở lượt mới".')
        old_deadline = attempt.deadline_at
        new_deadline = old_deadline + timedelta(minutes=minutes)
        try:
            self.repo.extend_attempt_deadline(attempt_id, new_deadline)
            self._log(
                attempt_id, "teacher_extend", teacher_id, reason, minutes=minutes,
                old_deadline=old_deadline.isoformat(), new_deadline=new_deadline.isoformat(),
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return new_deadline

    def extend_exam(self, exam_id: int, *, minutes: int, teacher_id: int, reason: str) -> int:
        """Gia hạn cả phòng: dời giờ đóng phòng và hạn của mọi em đang làm. Trả số lượt đã gia hạn."""
        reason, minutes = self._need_reason(reason), self._need_minutes(minutes)
        try:
            ids = list(
                self.db.scalars(
                    select(ExamAttempt.id)
                    .where(ExamAttempt.exam_id == exam_id, ExamAttempt.status == "in_progress")
                    .with_for_update()
                )
            )
            if self.repo.extend_exam_close(exam_id, minutes) != 1:
                raise InvalidTeacherAction("Không tìm thấy kỳ thi.")
            self.repo.extend_all_in_progress(exam_id, minutes)
            for attempt_id in ids:
                self._log(attempt_id, "teacher_extend_exam", teacher_id, reason, minutes=minutes)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return len(ids)

    # ----- buộc nộp, mở lại, mở lượt mới -----
    def force_submit(self, attempt_id: int, *, teacher_id: int, reason: str) -> SubmitResult:
        reason = self._need_reason(reason)
        result = self.attempts.force_submit(attempt_id, reason="teacher_force")
        self._log(attempt_id, "teacher_force_submit", teacher_id, reason, receipt=result.receipt_code)
        self.db.commit()
        return result

    def reopen_attempt(self, attempt_id: int, *, minutes: int, teacher_id: int, reason: str) -> datetime:
        """Mở lại lượt đã bị hệ thống tự chốt để em làm tiếp với đáp án đã lưu.

        Không mở lại bài em đã tự nộp: em đã chủ động kết thúc, cô dùng "mở lượt mới" nếu muốn cho làm lại.
        """
        reason, minutes = self._need_reason(reason), self._need_minutes(minutes)
        now = self.now_fn()
        attempt = self.repo.lock_attempt(attempt_id)
        if attempt is None:
            self.db.rollback()
            raise NotAllowedToEnter("Không tìm thấy lượt thi.")
        if attempt.status == "submitted":
            self.db.rollback()
            raise InvalidTeacherAction('Em đã tự nộp bài; dùng "mở lượt mới" nếu muốn cho làm lại.')
        if attempt.status != "auto_submitted":
            self.db.rollback()
            raise InvalidTeacherAction("Lượt thi đang làm, không cần mở lại.")
        previous_receipt = attempt.receipt_code
        new_deadline = now + timedelta(minutes=minutes)
        try:
            if self.repo.reopen_attempt(attempt_id, new_deadline) != 1:
                raise InvalidTeacherAction("Không mở lại được lượt thi.")
            self._log(
                attempt_id, "teacher_reopen", teacher_id, reason, minutes=minutes,
                previous_receipt=previous_receipt, new_deadline=new_deadline.isoformat(),
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return new_deadline

    def open_extra_attempt(
        self, exam_id: int, student_id: int, *, teacher_id: int, reason: str, minutes: int | None = None
    ) -> int:
        """Mở lượt mới (làm lại từ đầu) cho một em. Lượt có attempt_no lớn nhất là lượt tính điểm.

        Chỉ khi lượt hiện hành đã kết thúc. Hai lần bấm cùng lúc chỉ ra một lượt nhờ UNIQUE(exam, student, attempt_no).
        """
        reason = self._need_reason(reason)
        if minutes is not None:
            minutes = self._need_minutes(minutes)
        now = self.now_fn()
        exam = self.repo.get_exam(exam_id)
        if exam is None or exam.status != "published":
            self.db.rollback()
            raise InvalidTeacherAction("Kỳ thi chưa phát hành hoặc không tồn tại.")
        is_participant = self.db.scalar(
            select(ExamParticipant.student_id).where(
                ExamParticipant.exam_id == exam_id, ExamParticipant.student_id == student_id
            )
        )
        if is_participant is None:
            self.db.rollback()
            raise InvalidTeacherAction("Học sinh không có tên trong kỳ thi.")
        try:
            attempts = self.repo.lock_student_attempts(exam_id, student_id)
            if not attempts:
                raise InvalidTeacherAction("Em chưa vào thi; em tự bắt đầu được, không cần mở lượt mới.")
            if attempts[-1].status == "in_progress":
                raise InvalidTeacherAction("Lượt hiện tại còn đang làm; dùng gia hạn hoặc buộc nộp.")
            new_id = self.repo.insert_extra_attempt(
                exam_id=exam_id, student_id=student_id, attempt_no=attempts[-1].attempt_no + 1, now=now,
                deadline_at=now + timedelta(minutes=minutes or exam.duration_minutes), granted_by=teacher_id,
                reason=reason, shuffle_seed=secrets.randbits(62),
            )
            self._log(new_id, "teacher_grant", teacher_id, reason, previous_attempt_id=attempts[-1].id)
            self.db.commit()
            return new_id
        except IntegrityError as exc:
            self.db.rollback()
            raise InvalidTeacherAction("Lượt mới vừa được mở bởi một thao tác khác.") from exc
        except Exception:
            self.db.rollback()
            raise
