from app.core.base import Base
from sqlalchemy import Integer, Column, String, DateTime, ForeignKey

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    grade = Column(Integer, nullable=False)
    default_capacity = Column(Integer, nullable=False, default=85)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=True)

class ClassEnrollment(Base):
    __tablename__ = "class_enrollments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.user_id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=True)