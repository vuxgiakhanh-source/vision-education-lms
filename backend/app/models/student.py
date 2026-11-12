from app.core.base import Base
from sqlalchemy import Integer, Column, ForeignKey, CheckConstraint


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint(
            "grade IN (10, 11, 12)",
            name="ck_students_grade"
        ),
    )
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    grade = Column(Integer, nullable=False)
