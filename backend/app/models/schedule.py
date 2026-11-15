from app.core.base import Base
from sqlalchemy import CheckConstraint, String, Integer, Column, ForeignKey, DateTime, Boolean

class ClassSession(Base):
    __tablename__ = "class_sessions"
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ck_class_sessions_time_range"),
        CheckConstraint(
            "status IN ('scheduled', 'cancelled')",
            name="ck_class_sessions_status"
        )
    )
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    has_algebra = Column(Boolean, default=False)
    has_geometry = Column(Boolean, default=False)
    is_review = Column(Boolean, default=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="scheduled")

class SessionsTransfer(Base):
    __tablename__ = "sessions_transfers"
    student_id = Column(Integer, ForeignKey("students.user_id"), primary_key=True)
    original_session_id = Column(Integer, ForeignKey("class_sessions.id"), primary_key=True)
    replacement_sessions_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=True, default=None)