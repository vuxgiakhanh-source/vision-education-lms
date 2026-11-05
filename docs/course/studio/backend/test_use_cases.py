"""Observe state and scope, rather than counting internal function calls."""
from copy import deepcopy
import unittest
import singlefile
from storage import new_store
from use_cases import archive_class, create_class, list_classes


class UseCaseTests(unittest.TestCase):
    def setUp(self):
        self.store = new_store()
        self.teacher = {'id': 1, 'role': 'teacher'}
        self.other = {'id': 5, 'role': 'teacher'}
        self.student = {'id': 2, 'role': 'student'}

    def test_trim_and_owner_come_from_actor(self):
        row = create_class(self.store, self.teacher, '  Python  ')
        self.assertEqual(row, {'id': 1, 'title': 'Python', 'teacher_id': 1, 'status': 'active'})
        self.assertEqual(list_classes(self.store, self.teacher), [row])

    def test_invalid_title_does_not_consume_an_id_or_write(self):
        for title in [' ', None, 42, 'x' * 201]:
            before = deepcopy(self.store)
            with self.assertRaises(ValueError):
                create_class(self.store, self.teacher, title)
            self.assertEqual(self.store, before)
        self.assertEqual(create_class(self.store, self.teacher, 'Good')['id'], 1)

    def test_student_cannot_create_or_archive(self):
        row = create_class(self.store, self.teacher, 'Python')
        before = deepcopy(self.store)
        with self.assertRaises(PermissionError):
            create_class(self.store, self.student, 'No')
        with self.assertRaises(PermissionError):
            archive_class(self.store, self.student, row['id'])
        self.assertEqual(self.store, before)

    def test_teacher_list_is_scoped(self):
        one = create_class(self.store, self.teacher, 'A')
        two = create_class(self.store, self.other, 'B')
        self.assertEqual(list_classes(self.store, self.teacher), [one])
        self.assertEqual(list_classes(self.store, self.other), [two])

    def test_other_owner_and_unknown_id_leave_store_unchanged(self):
        row = create_class(self.store, self.teacher, 'A')
        before = deepcopy(self.store)
        for class_id in [row['id'], 999]:
            with self.assertRaises(LookupError):
                archive_class(self.store, self.other, class_id)
            self.assertEqual(self.store, before)

    def test_archive_preserves_identity_title_owner_and_history(self):
        old = create_class(self.store, self.teacher, 'Python')
        new = archive_class(self.store, self.teacher, old['id'])
        self.assertEqual(new, {**old, 'status': 'archived'})
        self.assertEqual(list_classes(self.store, self.teacher), [new])
        self.assertEqual(self.store['next_id'], 2)

    def test_archive_retry_is_unchanged(self):
        row = create_class(self.store, self.teacher, 'A')
        first = archive_class(self.store, self.teacher, row['id'])
        before = deepcopy(self.store)
        self.assertEqual(archive_class(self.store, self.teacher, row['id']), first)
        self.assertEqual(self.store, before)

    def test_returned_values_cannot_mutate_storage(self):
        row = create_class(self.store, self.teacher, 'Original')
        row['title'] = 'Changed outside'
        listed = list_classes(self.store, self.teacher)
        listed[0]['title'] = 'Changed again'
        self.assertEqual(list_classes(self.store, self.teacher)[0]['title'], 'Original')

    def test_split_preserves_create_and_list_behavior(self):
        old_store = singlefile.new_store()
        new_store_value = new_store()
        for actor, title in [(self.teacher, '  A  '), (self.other, 'B')]:
            self.assertEqual(singlefile.create_class(old_store, actor, title),
                             create_class(new_store_value, actor, title))
        self.assertEqual(singlefile.list_classes(old_store, self.teacher),
                         list_classes(new_store_value, self.teacher))


if __name__ == '__main__':
    unittest.main()
