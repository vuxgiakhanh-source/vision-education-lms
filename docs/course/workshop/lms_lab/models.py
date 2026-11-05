from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    role = Column(String(30), nullable=False)
    active = Column(Integer, nullable=False, default=1)


class Classroom(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)


class Membership(Base):
    __tablename__ = 'memberships'
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    __table_args__ = (UniqueConstraint('class_id', 'student_id', name='uq_membership'),)


class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    due_at = Column(DateTime, nullable=True)  # UTC by contract


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    answer = Column(String(2000), nullable=False)
    submitted_at = Column(DateTime, nullable=False)
    score = Column(Integer, nullable=True)
    grade_published = Column(Boolean, nullable=False, default=False)
    __table_args__ = (
        UniqueConstraint('assignment_id', 'student_id', name='uq_submission'),
        CheckConstraint('score IS NULL OR (score >= 0 AND score <= 10)', name='ck_submission_score'),
    )
