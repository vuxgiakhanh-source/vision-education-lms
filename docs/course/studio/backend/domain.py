"""Rules use values only; no terminal, database or imports from the UI."""


def normalize_title(title):
    if not isinstance(title, str):
        raise ValueError('Tên lớp phải là chuỗi')
    normalized = title.strip()
    if not 1 <= len(normalized) <= 200:
        raise ValueError('Tên lớp cần 1–200 ký tự sau khi bỏ khoảng trắng ngoài')
    return normalized


def require_teacher(actor):
    if actor['role'] != 'teacher':
        raise PermissionError('Chỉ giáo viên được thực hiện')


def require_owner(actor, classroom):
    require_teacher(actor)
    if classroom is None or classroom['teacher_id'] != actor['id']:
        raise LookupError('Không thấy lớp trong phạm vi của bạn')
