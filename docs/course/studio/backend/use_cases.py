"""Application operations; rules run before a memory write."""
from domain import normalize_title, require_owner, require_teacher
from storage import all_classes, find_class, insert_class, replace_class


def create_class(store, actor, title):
    require_teacher(actor)
    normalized = normalize_title(title)
    return insert_class(store, normalized, actor['id'])


def list_classes(store, actor):
    require_teacher(actor)
    return [row for row in all_classes(store) if row['teacher_id'] == actor['id']]


def archive_class(store, actor, class_id):
    require_teacher(actor)
    row = find_class(store, class_id)
    require_owner(actor, row)
    row['status'] = 'archived'
    return replace_class(store, row)
