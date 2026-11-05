from sqlalchemy import select
from .models import Classroom, Membership


class ClassRepository:
    def __init__(self, db):
        self.db = db

    def list_visible(self, actor, offset: int, limit: int):
        query = select(Classroom)
        if actor.role == 'teacher':
            query = query.where(Classroom.teacher_id == actor.id)
        else:
            query = query.join(Membership).where(Membership.student_id == actor.id)
        return list(self.db.scalars(query.order_by(Classroom.id).offset(offset).limit(limit)))

    def find(self, class_id: int):
        return self.db.get(Classroom, class_id)

    def is_member(self, class_id: int, actor_id: int) -> bool:
        query = select(Membership.id).where(
            Membership.class_id == class_id, Membership.student_id == actor_id)
        return self.db.scalar(query) is not None

    def add(self, classroom):
        self.db.add(classroom)
        self.db.flush()
