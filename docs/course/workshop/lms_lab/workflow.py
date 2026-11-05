"""Reference vertical slice. UTC timestamps; integer scores; no product imports."""
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Path, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from .models import Assignment, Classroom, Membership, Submission
from .service import Forbidden, NotFound
from .unit_of_work import SqlTransaction


class AssignmentInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=200)
    due_at: datetime | None = None

    @field_validator('title', mode='before')
    @classmethod
    def trim(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator('due_at')
    @classmethod
    def utc(cls, value):
        if value is not None and value.utcoffset() is None:
            raise ValueError('Deadline cần timezone')
        return value.astimezone(timezone.utc).replace(tzinfo=None) if value else None


class AnswerInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    answer: str = Field(min_length=1, max_length=2000)

    @field_validator('answer', mode='before')
    @classmethod
    def trim(cls, value):
        return value.strip() if isinstance(value, str) else value


class GradeInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    score: int = Field(ge=0, le=10, strict=True)
    publish: bool = Field(strict=True)


class AssignmentOutput(BaseModel):
    id: int
    class_id: int
    title: str
    due_at: datetime | None


class SubmissionOutput(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    answer: str
    submitted_at: datetime
    score: int | None
    grade_published: bool


class Conflict(Exception):
    pass


class TooLate(Exception):
    pass


def timestamp(value):
    return value.replace(tzinfo=timezone.utc) if value is not None else None


def assignment_output(row):
    return dict(id=row.id, class_id=row.class_id, title=row.title, due_at=timestamp(row.due_at))


def submission_output(row, teacher=False):
    return dict(id=row.id, assignment_id=row.assignment_id, student_id=row.student_id,
                answer=row.answer, submitted_at=timestamp(row.submitted_at),
                score=row.score if teacher or row.grade_published else None,
                grade_published=row.grade_published)


class WorkflowRepository:
    def __init__(self, db):
        self.db = db

    def classroom(self, class_id):
        return self.db.get(Classroom, class_id)

    def member(self, class_id, user_id):
        return self.db.scalar(select(Membership.id).where(
            Membership.class_id == class_id, Membership.student_id == user_id)) is not None

    def assignment(self, assignment_id, lock=False):
        query = select(Assignment).where(Assignment.id == assignment_id)
        return self.db.scalar(query.with_for_update() if lock else query)

    def assignments(self, class_id, offset, limit):
        return self.db.scalars(select(Assignment).where(Assignment.class_id == class_id)
                               .order_by(Assignment.id).offset(offset).limit(limit)).all()

    def mine(self, assignment_id, user_id, lock=False):
        # Locking read on MySQL: see latest committed row after acquiring assignment lock.
        query = select(Submission).where(Submission.assignment_id == assignment_id,
                                        Submission.student_id == user_id)
        return self.db.scalar(query.with_for_update() if lock else query)

    def submissions(self, assignment_id, offset, limit):
        return self.db.scalars(select(Submission).where(Submission.assignment_id == assignment_id)
                               .order_by(Submission.id).offset(offset).limit(limit)).all()

    def submission(self, submission_id):
        return self.db.scalar(select(Submission).where(Submission.id == submission_id).with_for_update())

    def add(self, row):
        self.db.add(row)
        self.db.flush()


class WorkflowService:
    def __init__(self, repository, transaction, now=None):
        self.repository = repository
        self.transaction = transaction
        self.now = now or (lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    def scope(self, actor, class_id, write=False):
        row = self.repository.classroom(class_id)
        if row is None:
            raise NotFound()
        if actor.role == 'teacher':
            if row.teacher_id != actor.id:
                raise NotFound()
        elif not self.repository.member(class_id, actor.id):
            raise NotFound()
        elif write:
            raise Forbidden()
        return row

    def require_assignment(self, actor, assignment_id, write=False, lock=False):
        row = self.repository.assignment(assignment_id, lock=lock)
        if row is None:
            raise NotFound()
        self.scope(actor, row.class_id, write)
        return row

    def create(self, actor, class_id, payload):
        self.scope(actor, class_id, write=True)
        row = Assignment(class_id=class_id, title=payload.title, due_at=payload.due_at)
        try:
            self.repository.add(row)
            self.transaction.commit()
        except Exception:
            self.transaction.rollback()
            raise
        return assignment_output(row)

    def submit(self, actor, assignment_id, answer):
        if actor.role != 'student':
            raise Forbidden()
        try:
            assignment = self.require_assignment(actor, assignment_id, lock=True)
            existing = self.repository.mine(assignment_id, actor.id, lock=True)
            if existing is not None:
                if existing.answer != answer:
                    raise Conflict()
                result = submission_output(existing)
            else:
                now = self.now()
                if assignment.due_at is not None and now > assignment.due_at:
                    raise TooLate()
                row = Submission(assignment_id=assignment_id, student_id=actor.id,
                                 answer=answer, submitted_at=now)
                self.repository.add(row)
                result = submission_output(row)
            self.transaction.commit()
            return result
        except Exception:
            self.transaction.rollback()
            raise

    def grade(self, actor, submission_id, payload):
        try:
            row = self.repository.submission(submission_id)
            if row is None:
                raise NotFound()
            self.require_assignment(actor, row.assignment_id, write=True)
            row.score, row.grade_published = payload.score, payload.publish
            self.transaction.commit()
            return submission_output(row, teacher=True)
        except Exception:
            self.transaction.rollback()
            raise


def install_workflow(app, get_db, current_user):
    def service(db=Depends(get_db)):
        return WorkflowService(WorkflowRepository(db), SqlTransaction(db))

    def execute(call):
        try:
            return call()
        except NotFound:
            raise HTTPException(404, 'Không tìm thấy trong phạm vi được phép') from None
        except Forbidden:
            raise HTTPException(403, 'Không đủ quyền') from None
        except Conflict:
            raise HTTPException(409, 'Đã có bài khác; không ghi đè bản gốc') from None
        except TooLate:
            raise HTTPException(409, 'Đã quá hạn nộp') from None

    @app.get('/me')
    def me(actor=Depends(current_user)):
        return dict(id=actor.id, name=actor.name, role=actor.role)

    @app.post('/classes/{class_id}/assignments', response_model=AssignmentOutput, status_code=201)
    def create(payload: AssignmentInput, class_id: int = Path(gt=0),
               actor=Depends(current_user), flow=Depends(service)):
        return execute(lambda: flow.create(actor, class_id, payload))

    @app.get('/classes/{class_id}/assignments', response_model=list[AssignmentOutput])
    def assignments(class_id: int = Path(gt=0), page: int = Query(1, ge=1),
                    page_size: int = Query(20, ge=1, le=100),
                    actor=Depends(current_user), flow=Depends(service)):
        execute(lambda: flow.scope(actor, class_id))
        return [assignment_output(row) for row in flow.repository.assignments(class_id, (page-1)*page_size, page_size)]

    @app.post('/assignments/{assignment_id}/submissions', response_model=SubmissionOutput)
    def submit(payload: AnswerInput, assignment_id: int = Path(gt=0),
               actor=Depends(current_user), flow=Depends(service)):
        return execute(lambda: flow.submit(actor, assignment_id, payload.answer))

    @app.get('/assignments/{assignment_id}/my-submission', response_model=SubmissionOutput | None)
    def mine(assignment_id: int = Path(gt=0), actor=Depends(current_user), flow=Depends(service)):
        if actor.role != 'student':
            raise HTTPException(403, 'Dùng danh sách bài nộp dành cho cô')
        execute(lambda: flow.require_assignment(actor, assignment_id))
        row = flow.repository.mine(assignment_id, actor.id)
        return submission_output(row) if row else None

    @app.get('/assignments/{assignment_id}/submissions', response_model=list[SubmissionOutput])
    def submissions(assignment_id: int = Path(gt=0), page: int = Query(1, ge=1),
                    page_size: int = Query(20, ge=1, le=100),
                    actor=Depends(current_user), flow=Depends(service)):
        execute(lambda: flow.require_assignment(actor, assignment_id, write=True))
        return [submission_output(row, teacher=True) for row in flow.repository.submissions(assignment_id, (page-1)*page_size, page_size)]

    @app.put('/submissions/{submission_id}/grade', response_model=SubmissionOutput)
    def grade(payload: GradeInput, submission_id: int = Path(gt=0),
              actor=Depends(current_user), flow=Depends(service)):
        return execute(lambda: flow.grade(actor, submission_id, payload))
