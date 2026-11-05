"""A disposable memory store. Restarting Python loses its data."""


def new_store():
    return {'next_id': 1, 'classes': {}}


def insert_class(store, title, teacher_id):
    class_id = store['next_id']
    row = {'id': class_id, 'title': title, 'teacher_id': teacher_id, 'status': 'active'}
    store['classes'][class_id] = row.copy()
    store['next_id'] += 1
    return row.copy()


def find_class(store, class_id):
    row = store['classes'].get(class_id)
    return None if row is None else row.copy()


def all_classes(store):
    return [row.copy() for row in store['classes'].values()]


def replace_class(store, row):
    if row['id'] not in store['classes']:
        raise LookupError('Không thể thay lớp chưa tồn tại')
    store['classes'][row['id']] = row.copy()
    return row.copy()
