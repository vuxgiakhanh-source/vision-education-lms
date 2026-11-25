"""Truy cập dữ liệu lượt thi. Mỗi hàm là một câu lệnh SQL có chủ đích (docs/design/exam-room-concurrency.md mục 4).

Đây là lớp MySQL: dùng INSERT ... ON DUPLICATE KEY UPDATE, SELECT ... FOR UPDATE SKIP LOCKED và
`rowcount` kiểu CLIENT_FOUND_ROWS. Test của lớp này phải chạy trên MySQL thật (SQLite bỏ qua khóa dòng).

Quy ước: repository không commit. Service quyết định ranh giới giao dịch.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import exists, func, select, text, update
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from app.models.exam import (
    Exam,
    ExamAnswerKey,
    ExamAttempt,
    ExamAttemptEvent,
    ExamGradeHistory,
    ExamLateSubmission,
    ExamParticipant,
)
from app.models.user import User


class AttemptRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ----- bắt đầu hoặc tiếp tục -----
    def get_exam_for_participant(self, exam_id: int, student_id: int) -> Row | None:
        """Quyền và cửa sổ thi trong một câu: kỳ thi tồn tại VÀ em có tên trong danh sách."""
        return self.db.execute(
            select(
                Exam.id, Exam.status, Exam.opens_at, Exam.closes_at,
                Exam.duration_minutes, Exam.paper_id,
            )
            .join(ExamParticipant, ExamParticipant.exam_id == Exam.id)
            .where(Exam.id == exam_id, ExamParticipant.student_id == student_id)
        ).first()

    def create_first_attempt_if_absent(
        self, *, exam_id: int, student_id: int, now: datetime, deadline_at: datetime,
        device_id: str | None, shuffle_seed: int,
    ) -> None:
        """Bấm "Bắt đầu" lặp hay nhiều tab cùng lúc vẫn chỉ có một dòng nhờ UNIQUE(exam, student, attempt_no).

        ON DUPLICATE KEY UPDATE id = id là phép không đổi gì: giữ nguyên hạn nộp và hạt giống của lượt đã có.
        """
        stmt = mysql_insert(ExamAttempt).values(
            exam_id=exam_id, student_id=student_id, attempt_no=1, started_at=now,
            deadline_at=deadline_at, status="in_progress", answers={}, answers_version=0,
            write_epoch=1, device_id=device_id, shuffle_seed=shuffle_seed,
            last_seen_at=now,
        )
        self.db.execute(stmt.on_duplicate_key_update(id=ExamAttempt.id))

    def get_current_attempt(self, exam_id: int, student_id: int) -> ExamAttempt | None:
        """Lượt tính điểm của em: attempt_no lớn nhất. Luôn đọc lại từ DB, không dùng bản trong phiên."""
        return self.db.scalars(
            select(ExamAttempt)
            .where(ExamAttempt.exam_id == exam_id, ExamAttempt.student_id == student_id)
            .order_by(ExamAttempt.attempt_no.desc())
            .limit(1)
            .execution_options(populate_existing=True)
        ).first()

    def get_attempt(self, attempt_id: int) -> ExamAttempt | None:
        return self.db.scalars(
            select(ExamAttempt).where(ExamAttempt.id == attempt_id).execution_options(populate_existing=True)
        ).first()

    def is_student_active(self, student_id: int) -> bool:
        return bool(self.db.scalar(select(User.is_active).where(User.id == student_id)))

    # ----- lưu bài: một câu lệnh -----
    def save_answers(
        self, *, attempt_id: int, student_id: int, epoch: int, base_version: int,
        answers: dict[str, Any], now: datetime, grace_floor: datetime,
        current_item: str | None, item_ms: dict[str, int] | None,
        away_count: int, away_ms: int, fullscreen_exit_count: int, offline_count: int,
    ) -> int:
        """Ghi toàn bộ đáp án nếu và chỉ nếu mọi điều kiện còn đúng. Trả số dòng khớp (1 hoặc 0).

        Mọi điều kiện (đúng chủ bài, còn đang làm, đúng quyền ghi, đúng phiên bản, còn hạn, tài khoản còn hoạt
        động) nằm TRONG câu lệnh, nên không có khe hở giữa kiểm tra và ghi. Bộ đếm dùng GREATEST để gửi lại
        cùng giá trị hay gửi lệch thứ tự đều không làm số lùi.
        """
        result = self.db.execute(
            update(ExamAttempt)
            .where(
                ExamAttempt.id == attempt_id,
                ExamAttempt.student_id == student_id,
                ExamAttempt.status == "in_progress",
                ExamAttempt.write_epoch == epoch,
                ExamAttempt.answers_version == base_version,
                ExamAttempt.deadline_at >= grace_floor,
                exists().where(User.id == ExamAttempt.student_id, User.is_active.is_(True)),
            )
            .values(
                answers=answers,
                answers_version=ExamAttempt.answers_version + 1,
                last_sync_at=now,
                last_seen_at=now,
                current_item=current_item,
                item_ms=item_ms,
                away_count=func.greatest(ExamAttempt.away_count, away_count),
                away_ms=func.greatest(ExamAttempt.away_ms, away_ms),
                fullscreen_exit_count=func.greatest(ExamAttempt.fullscreen_exit_count, fullscreen_exit_count),
                offline_count=func.greatest(ExamAttempt.offline_count, offline_count),
            )
            .execution_options(synchronize_session=False)
        )
        return result.rowcount

    def touch(self, attempt_id: int, now: datetime) -> None:
        self.db.execute(
            update(ExamAttempt).where(ExamAttempt.id == attempt_id).values(last_seen_at=now)
            .execution_options(synchronize_session=False)
        )

    def take_over_write(self, *, attempt_id: int, student_id: int, device_id: str, now: datetime) -> int:
        """Chuyển quyền ghi sang thiết bị mới: tăng epoch để máy cũ bị từ chối ở lần lưu kế tiếp."""
        result = self.db.execute(
            update(ExamAttempt)
            .where(
                ExamAttempt.id == attempt_id, ExamAttempt.student_id == student_id,
                ExamAttempt.status == "in_progress",
            )
            .values(write_epoch=ExamAttempt.write_epoch + 1, device_id=device_id, last_seen_at=now)
            .execution_options(synchronize_session=False)
        )
        return result.rowcount

    # ----- nộp bài và chốt -----
    def lock_attempt(self, attempt_id: int, student_id: int | None = None) -> ExamAttempt | None:
        """Khóa dòng lượt thi của CHÍNH em đó (không bao giờ khóa bảng kỳ thi dùng chung)."""
        stmt = select(ExamAttempt).where(ExamAttempt.id == attempt_id)
        if student_id is not None:
            stmt = stmt.where(ExamAttempt.student_id == student_id)
        return self.db.scalars(stmt.with_for_update().execution_options(populate_existing=True)).first()

    def get_answer_key(self, paper_id: int) -> ExamAnswerKey | None:
        return self.db.scalars(
            select(ExamAnswerKey).where(ExamAnswerKey.paper_id == paper_id).execution_options(populate_existing=True)
        ).first()

    def get_paper_id_for_attempt(self, exam_id: int) -> int | None:
        return self.db.scalar(select(Exam.paper_id).where(Exam.id == exam_id))

    def finalize(
        self, *, attempt_id: int, status: str, answers: dict[str, Any], now: datetime,
        request_id: str | None, receipt_code: str, digest: str, score: Any, max_score: Any,
    ) -> None:
        """Chuyển lượt sang đã nộp. Gọi trong giao dịch đã khóa dòng; WHERE status giữ nó chỉ chạy được một lần."""
        result = self.db.execute(
            update(ExamAttempt)
            .where(ExamAttempt.id == attempt_id, ExamAttempt.status == "in_progress")
            .values(
                status=status, answers=answers, answers_version=ExamAttempt.answers_version + 1,
                submitted_at=now, submit_request_id=request_id, receipt_code=receipt_code,
                content_digest=digest, score=score, max_score=max_score,
            )
            .execution_options(synchronize_session=False)
        )
        if result.rowcount != 1:
            raise RuntimeError("Lượt thi không còn ở trạng thái đang làm khi chốt.")

    def add_grade_history(
        self, *, attempt_id: int, key_version: int, score: Any, now: datetime, reason: str
    ) -> None:
        self.db.add(
            ExamGradeHistory(
                attempt_id=attempt_id, answer_key_version=key_version, score=score,
                graded_at=now, reason=reason,
            )
        )

    def add_late_submission(
        self, *, attempt_id: int, answers: dict[str, Any], now: datetime, reason: str
    ) -> None:
        self.db.add(
            ExamLateSubmission(
                attempt_id=attempt_id, answers=answers, received_at=now, reason=reason,
                decision="pending",
            )
        )

    # ----- quét chốt -----
    def lock_expired_attempt_ids(self, *, cutoff: datetime, limit: int) -> list[int]:
        """Khóa tối đa `limit` lượt quá hạn. SKIP LOCKED: lượt đang được em nộp hoặc người quét khác giữ thì bỏ qua."""
        rows = self.db.execute(
            select(ExamAttempt.id)
            .where(ExamAttempt.status == "in_progress", ExamAttempt.deadline_at < cutoff)
            .order_by(ExamAttempt.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        ).all()
        return [r[0] for r in rows]

    # ----- sự kiện từ trình duyệt -----
    def count_events(self, attempt_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(ExamAttemptEvent).where(ExamAttemptEvent.attempt_id == attempt_id)
        )

    def max_client_seq(self, attempt_id: int) -> int:
        return self.db.scalar(
            select(func.coalesce(func.max(ExamAttemptEvent.client_seq), 0)).where(ExamAttemptEvent.attempt_id == attempt_id)
        )

    def add_event(
        self, *, attempt_id: int, type: str, now: datetime, client_seq: int | None = None,
        client_offset_ms: int | None = None, payload: dict[str, Any] | None = None,
    ) -> None:
        self.db.add(
            ExamAttemptEvent(
                attempt_id=attempt_id, type=type, client_seq=client_seq,
                client_offset_ms=client_offset_ms, server_at=now, payload=payload,
            )
        )

    # ----- thao tác của giáo viên -----
    def extend_attempt_deadline(self, attempt_id: int, new_deadline: datetime) -> int:
        """Chỉ gia hạn lượt đang làm và chỉ kéo dài ra (không rút ngắn)."""
        result = self.db.execute(
            update(ExamAttempt)
            .where(ExamAttempt.id == attempt_id, ExamAttempt.status == "in_progress", ExamAttempt.deadline_at < new_deadline)
            .values(deadline_at=new_deadline)
            .execution_options(synchronize_session=False)
        )
        return result.rowcount

    def extend_all_in_progress(self, exam_id: int, minutes: int) -> int:
        """Gia hạn mọi lượt đang làm của kỳ thi bằng một câu lệnh."""
        result = self.db.execute(
            update(ExamAttempt)
            .where(ExamAttempt.exam_id == exam_id, ExamAttempt.status == "in_progress")
            .values(deadline_at=func.date_add(ExamAttempt.deadline_at, text(f"INTERVAL {int(minutes)} MINUTE")))
            .execution_options(synchronize_session=False)
        )
        return result.rowcount

    def extend_exam_close(self, exam_id: int, minutes: int) -> int:
        """Dời giờ đóng phòng để em vào muộn sau này cũng được tính theo giờ mới."""
        result = self.db.execute(
            update(Exam)
            .where(Exam.id == exam_id)
            .values(
                closes_at=func.date_add(Exam.closes_at, text(f"INTERVAL {int(minutes)} MINUTE")),
                version=Exam.version + 1,
            )
            .execution_options(synchronize_session=False)
        )
        return result.rowcount

    def reopen_attempt(self, attempt_id: int, new_deadline: datetime) -> int:
        """Mở lại lượt đã bị hệ thống tự chốt để em làm tiếp, giữ nguyên đáp án đã lưu.

        Tăng write_epoch để mọi thiết bị đã mất quyền phải đồng bộ lại. Xóa biên nhận cũ vì bài chưa còn là bản nộp.
        """
        result = self.db.execute(
            update(ExamAttempt)
            .where(ExamAttempt.id == attempt_id, ExamAttempt.status == "auto_submitted")
            .values(
                status="in_progress", deadline_at=new_deadline, write_epoch=ExamAttempt.write_epoch + 1,
                receipt_code=None, submitted_at=None, content_digest=None, submit_request_id=None,
                score=None, max_score=None,
            )
            .execution_options(synchronize_session=False)
        )
        return result.rowcount

    def lock_student_attempts(self, exam_id: int, student_id: int) -> list[ExamAttempt]:
        """Khóa mọi lượt của em trong kỳ thi để hai lần bấm "mở lượt mới" không cùng tính ra một số lượt."""
        return list(
            self.db.scalars(
                select(ExamAttempt)
                .where(ExamAttempt.exam_id == exam_id, ExamAttempt.student_id == student_id)
                .order_by(ExamAttempt.attempt_no)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
        )

    def insert_extra_attempt(
        self, *, exam_id: int, student_id: int, attempt_no: int, now: datetime, deadline_at: datetime,
        granted_by: int, reason: str, shuffle_seed: int,
    ) -> int:
        attempt = ExamAttempt(
            exam_id=exam_id, student_id=student_id, attempt_no=attempt_no, started_at=now, deadline_at=deadline_at,
            status="in_progress", answers={}, answers_version=0, write_epoch=1, shuffle_seed=shuffle_seed,
            granted_by=granted_by, grant_reason=reason[:200], last_seen_at=None,
        )
        self.db.add(attempt)
        self.db.flush()
        return attempt.id

    def get_exam(self, exam_id: int) -> Exam | None:
        return self.db.scalars(select(Exam).where(Exam.id == exam_id).execution_options(populate_existing=True)).first()
