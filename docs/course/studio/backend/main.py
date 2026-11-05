from storage import new_store
from use_cases import archive_class, create_class, list_classes


def main():
    store = new_store()
    teacher = {'id': 1, 'role': 'teacher'}
    other_teacher = {'id': 5, 'role': 'teacher'}
    created = create_class(store, teacher, '  Python  ')
    print('Đã tạo:', created['id'], created['title'], created['status'])
    archived = archive_class(store, teacher, created['id'])
    print('Đã lưu trữ:', archived['status'])
    print('Lịch sử của cô:', len(list_classes(store, teacher)))
    print('Lớp của cô khác:', len(list_classes(store, other_teacher)))


if __name__ == '__main__':
    main()
