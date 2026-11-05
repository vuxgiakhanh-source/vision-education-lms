"""Worked attendance rule: no HTTP, SQLAlchemy, token, or global mutable sheet."""
from dataclasses import dataclass, replace


STATUSES = {'present', 'late', 'absent', 'excused'}


class InvalidInput(ValueError):
    pass


class Forbidden(Exception):
    pass


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


@dataclass(frozen=True)
class Actor:
    id: int
    role: str
    active: bool = True


@dataclass(frozen=True)
class Mark:
    student_id: int
    status: str | None


@dataclass(frozen=True)
class Sheet:
    id: int
    class_id: int
    teacher_id: int
    revision: int
    marks: tuple[Mark, ...]


def normalized_marks(marks, expected_ids):
    """Validate before turning a list into a dict: duplicate ids must not vanish."""
    if not 1 <= len(marks) <= 100:
        raise InvalidInput('Bai lab nhan 1..100 hoc sinh')
    ids = []
    result = []
    for mark in marks:
        if type(mark.student_id) is not int or mark.student_id <= 0:
            raise InvalidInput('student_id phai la so nguyen duong')
        if not isinstance(mark.status, str) or mark.status not in STATUSES:
            raise InvalidInput('Trang thai khong hop le hoac chua duoc chon')
        ids.append(mark.student_id)
        result.append(mark)
    if len(set(ids)) != len(ids):
        raise InvalidInput('Trung hoc sinh trong request')
    if set(ids) != set(expected_ids):
        raise InvalidInput('Phai gui dung toan bo danh sach cua buoi')
    return tuple(sorted(result, key=lambda item: item.student_id))


class AttendanceService:
    """Store.load returns one immutable snapshot; replace is atomic compare-and-set."""
    def __init__(self, store):
        self.store = store

    def read(self, actor: Actor, sheet_id: int) -> Sheet:
        if not actor.active or actor.role != 'teacher':
            raise Forbidden('Can giao vien dang hoat dong')
        sheet = self.store.load(sheet_id)
        if sheet is None or sheet.teacher_id != actor.id:
            raise NotFound('Khong co buoi trong pham vi duoc phep')
        return sheet

    def save(self, actor: Actor, sheet_id: int, base_revision: int,
             marks: tuple[Mark, ...]) -> Sheet:
        current = self.read(actor, sheet_id)
        if type(base_revision) is not int or base_revision < 0:
            raise InvalidInput('revision phai la so nguyen khong am')
        normalized = normalized_marks(marks, [m.student_id for m in current.marks])
        # A lost response may be retried. Identical state is already confirmed.
        if normalized == current.marks:
            return current
        if base_revision != current.revision:
            raise Conflict('Danh sach da thay doi; tai lai truoc khi sua')
        next_sheet = replace(current, revision=current.revision + 1, marks=normalized)
        if self.store.replace(current.revision, next_sheet):
            return next_sheet
        # Another request won after our read. Recheck the same-content retry.
        latest = self.read(actor, sheet_id)
        if normalized == latest.marks:
            return latest
        raise Conflict('Mot request khac da luu truoc')
