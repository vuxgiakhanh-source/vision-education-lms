from .models import Classroom
from .unit_of_work import Transaction


class Forbidden(Exception):
    pass


class NotFound(Exception):
    pass


class ClassService:
    def __init__(self, repository, transaction: Transaction):
        self.repository = repository
        self.transaction = transaction

    def list_visible(self, actor, page: int, page_size: int):
        return self.repository.list_visible(actor, (page - 1) * page_size, page_size)

    def read(self, actor, class_id: int):
        classroom = self.repository.find(class_id)
        if classroom is None:
            raise NotFound()
        visible = classroom.teacher_id == actor.id if actor.role == 'teacher' else (
            self.repository.is_member(class_id, actor.id))
        if not visible:
            raise NotFound()
        return classroom

    def create(self, actor, title: str):
        if actor.role != 'teacher':
            raise Forbidden()
        title = title.strip()
        if not 1 <= len(title) <= 200:
            raise ValueError('Tên lớp không hợp lệ')
        classroom = Classroom(title=title, teacher_id=actor.id)
        try:
            self.repository.add(classroom)
            self.transaction.commit()
        except Exception:
            self.transaction.rollback()
            raise
        return classroom

    def rename(self, actor, class_id: int, title: str):
        classroom = self.read(actor, class_id)
        if actor.role != 'teacher' or classroom.teacher_id != actor.id:
            raise Forbidden()
        title = title.strip()
        if not 1 <= len(title) <= 200:
            raise ValueError('Tên lớp không hợp lệ')
        try:
            classroom.title = title
            self.transaction.commit()
        except Exception:
            self.transaction.rollback()
            raise
        return classroom
