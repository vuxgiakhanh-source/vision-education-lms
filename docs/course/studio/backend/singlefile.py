"""Version before the archive requirement; kept for a before/after comparison."""


def new_store():
    return {'next_id': 1, 'classes': {}}


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


def create_class(store, actor, title):
    require_teacher(actor)
    normalized = normalize_title(title)
    class_id = store['next_id']
    row = {'id': class_id, 'title': normalized, 'teacher_id': actor['id'], 'status': 'active'}
    store['classes'][class_id] = row.copy()
    store['next_id'] += 1
    return row.copy()


def list_classes(store, actor):
    require_teacher(actor)
    return [row.copy() for row in store['classes'].values()
            if row['teacher_id'] == actor['id']]


def main():
    store = new_store()
    teacher = {'id': 1, 'role': 'teacher'}
    created = create_class(store, teacher, '  Python  ')
    print('Đã tạo:', created['id'], created['title'], created['status'])
    print('Số lớp của cô:', len(list_classes(store, teacher)))


if __name__ == '__main__':
    main()
