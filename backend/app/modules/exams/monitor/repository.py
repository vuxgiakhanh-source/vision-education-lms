"""Truy vấn cho màn theo dõi của giáo viên: MỘT câu lấy mọi em, không cộng dồn từ nhật ký sự kiện."""

from __future__ import annotations

from sqlalchemy import and_, func, select
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from app.models.exam import ExamAttempt, ExamParticipant
from app.models.user import User


class MonitorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_participants_with_latest_attempt(self, exam_id: int) -> list[Row]:
        """Mọi người có tên trong kỳ thi kèm lượt hiện hành (attempt_no lớn nhất), kể cả em chưa vào.

        Không kéo cột đáp án (JSON) về: 500 em x vài KB mỗi lần cô làm mới là vô ích. Số câu đã trả lời lấy bằng
        JSON_LENGTH ngay trong MySQL.
        """
        latest = (
            select(
                ExamAttempt.exam_id.label("exam_id"),
                ExamAttempt.student_id.label("student_id"),
                func.max(ExamAttempt.attempt_no).label("attempt_no"),
            )
            .where(ExamAttempt.exam_id == exam_id)
            .group_by(ExamAttempt.exam_id, ExamAttempt.student_id)
            .subquery()
        )
        stmt = (
            select(
                ExamParticipant.student_id,
                User.full_name,
                ExamAttempt.id.label("attempt_id"),
                ExamAttempt.attempt_no,
                ExamAttempt.status,
                ExamAttempt.started_at,
                ExamAttempt.deadline_at,
                ExamAttempt.last_seen_at,
                ExamAttempt.submitted_at,
                ExamAttempt.current_item,
                ExamAttempt.score,
                ExamAttempt.max_score,
                ExamAttempt.away_count,
                ExamAttempt.away_ms,
                ExamAttempt.fullscreen_exit_count,
                ExamAttempt.offline_count,
                ExamAttempt.grant_reason,
                func.json_length(ExamAttempt.answers).label("answered"),
            )
            .select_from(ExamParticipant)
            .join(User, User.id == ExamParticipant.student_id)
            .outerjoin(
                latest,
                and_(latest.c.exam_id == ExamParticipant.exam_id, latest.c.student_id == ExamParticipant.student_id),
            )
            .outerjoin(
                ExamAttempt,
                and_(
                    ExamAttempt.exam_id == latest.c.exam_id,
                    ExamAttempt.student_id == latest.c.student_id,
                    ExamAttempt.attempt_no == latest.c.attempt_no,
                ),
            )
            .where(ExamParticipant.exam_id == exam_id)
            .order_by(User.full_name, ExamParticipant.student_id)
        )
        return list(self.db.execute(stmt).all())
