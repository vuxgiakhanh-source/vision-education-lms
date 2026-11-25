"""Bảng của Phòng thi ảo. Thiết kế: docs/design/exam-room.md mục 4.

Quy ước:
- Giờ là giờ Việt Nam không múi giờ, luôn lấy từ core.clock.center_local_now().
- Trạng thái dùng String kèm CheckConstraint (đổi giá trị không cần ALTER ENUM).
- `version` là khóa lạc quan: mọi UPDATE sửa đề/kỳ thi phải kèm WHERE version = :đã_đọc.
"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class ExamSourceFile(Base):
    """Tệp đề cô tải lên. UNIQUE(owner_id, sha256) để tải trùng không tạo bản thứ hai."""

    __tablename__ = "exam_source_files"
    __table_args__ = (
        UniqueConstraint("owner_id", "sha256", name="uq_exam_source_files_owner_sha256"),
        CheckConstraint("kind IN ('pdf', 'docx', 'doc', 'xlsx')", name="ck_exam_source_files_kind"),
    )
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    kind = Column(String(8), nullable=False)
    original_name = Column(String(255), nullable=False)
    sha256 = Column(String(64), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    page_count = Column(Integer, nullable=True)
    storage_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False)


class ExamImportJob(Base):
    """Việc đọc đề chạy ở tiến trình khác. request_id UNIQUE để gửi lại không tạo việc thứ hai."""

    __tablename__ = "exam_import_jobs"
    __table_args__ = (
        UniqueConstraint("request_id", name="uq_exam_import_jobs_request_id"),
        Index("ix_exam_import_jobs_status_id", "status", "id"),
        CheckConstraint("mode IN ('direct', 'ai')", name="ck_exam_import_jobs_mode"),
        CheckConstraint(
            "status IN ('queued', 'running', 'done', 'failed')", name="ck_exam_import_jobs_status"
        ),
    )
    id = Column(Integer, primary_key=True)
    source_file_id = Column(Integer, ForeignKey("exam_source_files.id"), nullable=False)
    mode = Column(String(10), nullable=False, default="direct")
    status = Column(String(10), nullable=False, default="queued")
    progress = Column(Integer, nullable=False, default=0)
    result = Column(JSON, nullable=True)
    error = Column(JSON, nullable=True)
    request_id = Column(String(64), nullable=False)
    locked_until = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)


class ExamPaper(Base):
    """Đề. `structure` (IR) bất biến khi status = locked."""

    __tablename__ = "exam_papers"
    __table_args__ = (
        CheckConstraint("kind IN ('pdf', 'structured')", name="ck_exam_papers_kind"),
        CheckConstraint("status IN ('draft', 'locked')", name="ck_exam_papers_status"),
    )
    id = Column(Integer, primary_key=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    source_file_id = Column(Integer, ForeignKey("exam_source_files.id"), nullable=True)
    kind = Column(String(12), nullable=False)
    structure = Column(JSON, nullable=False)
    structure_hash = Column(String(64), nullable=False)
    status = Column(String(10), nullable=False, default="draft")
    locked_at = Column(DateTime, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False)


class ExamAnswerKey(Base):
    """Khóa đáp án nằm bảng riêng: API học sinh không bao giờ join bảng này."""

    __tablename__ = "exam_answer_keys"
    paper_id = Column(Integer, ForeignKey("exam_papers.id"), primary_key=True)
    key = Column(JSON, nullable=False)
    scoring = Column(JSON, nullable=False)
    version = Column(Integer, nullable=False, default=1)


class Exam(Base):
    """Kỳ thi: một đề, một cửa sổ thời gian, một danh sách người dự thi."""

    __tablename__ = "exams"
    __table_args__ = (
        Index("ix_exams_status_opens_at", "status", "opens_at"),
        CheckConstraint("opens_at < closes_at", name="ck_exams_window"),
        CheckConstraint("duration_minutes > 0", name="ck_exams_duration"),
        CheckConstraint("status IN ('draft', 'published', 'cancelled')", name="ck_exams_status"),
        CheckConstraint(
            "status = 'draft' OR (paper_id IS NOT NULL AND title IS NOT NULL "
            "AND opens_at IS NOT NULL AND closes_at IS NOT NULL AND duration_minutes IS NOT NULL)",
            name="ck_exams_complete_outside_draft",
        ),
        UniqueConstraint("created_by", "autosave_key", name="uq_exams_owner_autosave_key"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    paper_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("exam_papers.id"), nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    opens_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closes_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    schedule_inputs: Mapped[dict[str, str] | None] = mapped_column(JSON(none_as_null=True), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    late_entry_policy: Mapped[str] = mapped_column(String(20), nullable=False, default="cut_at_close")
    results_visible_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="draft")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    autosave_key: Mapped[str | None] = mapped_column(String(36), nullable=True)
    discarded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ExamParticipant(Base):
    """Chỉ người có tên ở đây mới vào được phòng. Khóa chính (exam_id, student_id) chặn thêm trùng."""

    __tablename__ = "exam_participants"
    __table_args__ = (
        CheckConstraint("added_via IN ('class', 'student')", name="ck_exam_participants_added_via"),
    )
    exam_id = Column(Integer, ForeignKey("exams.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    added_via = Column(String(10), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)


class ExamAttempt(Base):
    """Lượt thi của một học sinh.

    UNIQUE(exam_id, student_id, attempt_no): lượt đầu luôn có attempt_no = 1 nên bấm "Bắt đầu" lặp vẫn chỉ ra một dòng.
    Cô mở lượt mới cho em (làm lại từ đầu) thì thêm dòng attempt_no + 1; lượt có số lớn nhất là lượt tính điểm.
    "Mở lại lượt cũ" (gia hạn để làm tiếp) không tạo dòng mới.
    """

    __tablename__ = "exam_attempts"
    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", "attempt_no", name="uq_exam_attempts_exam_student_no"),
        UniqueConstraint("receipt_code", name="uq_exam_attempts_receipt_code"),
        Index("ix_exam_attempts_exam_status", "exam_id", "status"),
        # quét chốt các lượt quá hạn (sweeper)
        Index("ix_exam_attempts_status_deadline", "status", "deadline_at"),
        CheckConstraint(
            "status IN ('in_progress', 'submitted', 'auto_submitted')", name="ck_exam_attempts_status"
        ),
    )
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attempt_no = Column(Integer, nullable=False, default=1, server_default="1")
    # Chỉ có khi cô mở lượt mới cho em.
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    grant_reason = Column(String(200), nullable=True)
    started_at = Column(DateTime, nullable=False)
    deadline_at = Column(DateTime, nullable=False)
    status = Column(String(14), nullable=False, default="in_progress")
    answers = Column(JSON, nullable=False)
    answers_version = Column(Integer, nullable=False, default=0)
    # Tăng mỗi lần chuyển quyền ghi sang thiết bị khác; máy cũ gửi epoch cũ sẽ bị từ chối.
    write_epoch = Column(Integer, nullable=False, default=1)
    device_id = Column(String(64), nullable=True)
    # Hạt giống tráo câu/phương án, chốt lúc bắt đầu và không đổi (xem domain/shuffle.py).
    shuffle_seed = Column(BigInteger, nullable=True)
    last_sync_at = Column(DateTime, nullable=True)
    last_seen_at = Column(DateTime, nullable=True)
    # Số liệu cho cô theo dõi. Do trình duyệt báo, chỉ để cân nhắc, không tự trừ điểm hay khóa bài.
    # Lưu thẳng trên dòng lượt thi để màn giám sát chỉ đọc một bảng, không cộng dồn từ nhật ký sự kiện.
    current_item = Column(String(40), nullable=True)
    item_ms = Column(JSON, nullable=True)  # {"<mã câu>": số mili giây dừng ở câu, chỉ tính khi tab sáng}
    away_count = Column(Integer, nullable=False, default=0, server_default="0")  # lần ẩn tab/mất tiêu điểm
    away_ms = Column(BigInteger, nullable=False, default=0, server_default="0")
    fullscreen_exit_count = Column(Integer, nullable=False, default=0, server_default="0")
    offline_count = Column(Integer, nullable=False, default=0, server_default="0")
    submitted_at = Column(DateTime, nullable=True)
    submit_request_id = Column(String(64), nullable=True)
    receipt_code = Column(String(16), nullable=True)
    content_digest = Column(String(64), nullable=True)
    score = Column(Numeric(6, 2), nullable=True)
    max_score = Column(Numeric(6, 2), nullable=True)


class ExamAttemptEvent(Base):
    __tablename__ = "exam_attempt_events"
    __table_args__ = (Index("ix_exam_attempt_events_attempt_id_id", "attempt_id", "id"),)
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.id"), nullable=False)
    type = Column(String(30), nullable=False)
    client_seq = Column(Integer, nullable=True)
    client_offset_ms = Column(Integer, nullable=True)
    server_at = Column(DateTime, nullable=False)
    payload = Column(JSON, nullable=True)


class ExamLateSubmission(Base):
    """Phần bài đến sau hạn ân hạn. Không tự thành bài chính thức; cô quyết định."""

    __tablename__ = "exam_late_submissions"
    __table_args__ = (
        Index("ix_exam_late_submissions_attempt_id", "attempt_id"),
        CheckConstraint(
            "decision IN ('pending', 'accepted', 'rejected')", name="ck_exam_late_submissions_decision"
        ),
    )
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.id"), nullable=False)
    answers = Column(JSON, nullable=False)
    received_at = Column(DateTime, nullable=False)
    reason = Column(String(100), nullable=True)
    decision = Column(String(10), nullable=False, default="pending")
    decided_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class ExamGradeHistory(Base):
    """Lịch sử chấm: chấm lại khi sửa đáp án thì thêm dòng, không ghi đè."""

    __tablename__ = "exam_grade_history"
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.id"), nullable=False, index=True)
    answer_key_version = Column(Integer, nullable=False)
    score = Column(Numeric(6, 2), nullable=False)
    graded_at = Column(DateTime, nullable=False)
    reason = Column(String(30), nullable=False)
