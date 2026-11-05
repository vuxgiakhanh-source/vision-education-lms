import unittest
from dataclasses import replace
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from core import Actor, AttendanceService, Conflict, Forbidden, InvalidInput, Mark, NotFound
from storage import MarkRow, SqlStore, make_lab_engine, seed_demo


class AttendanceTests(unittest.TestCase):
    def setUp(self):
        self.engine = make_lab_engine()
        seed_demo(self.engine)
        self.store = SqlStore(self.engine)
        self.service = AttendanceService(self.store)
        self.teacher = Actor(1, 'teacher')
        self.marks = (Mark(2, 'present'), Mark(3, 'absent'))

    def tearDown(self):
        self.engine.dispose()

    def test_initial_null_is_not_absent(self):
        self.assertEqual([m.status for m in self.service.read(self.teacher, 42).marks],
                         [None, None])

    def test_save_then_retry_is_same_revision(self):
        saved = self.service.save(self.teacher, 42, 0, self.marks)
        retried = self.service.save(self.teacher, 42, 0, tuple(reversed(self.marks)))
        self.assertEqual(saved.revision, 1)
        self.assertEqual(saved, retried)
        self.assertEqual(self.store.load(42), saved)

    def test_old_revision_different_content_is_conflict(self):
        saved = self.service.save(self.teacher, 42, 0, self.marks)
        with self.assertRaises(Conflict):
            self.service.save(self.teacher, 42, 0, (Mark(2, 'late'), Mark(3, 'absent')))
        self.assertEqual(self.store.load(42), saved)

    def test_fresh_revision_can_edit(self):
        self.service.save(self.teacher, 42, 0, self.marks)
        changed = self.service.save(self.teacher, 42, 1,
                                    (Mark(2, 'late'), Mark(3, 'excused')))
        self.assertEqual(changed.revision, 2)

    def test_permission_checks_before_write(self):
        for actor, error in [(Actor(2, 'student'), Forbidden),
                             (Actor(1, 'teacher', False), Forbidden),
                             (Actor(9, 'teacher'), NotFound)]:
            with self.subTest(actor=actor):
                with self.assertRaises(error):
                    self.service.save(actor, 42, 0, self.marks)
        self.assertEqual(self.store.load(42).revision, 0)

    def test_invalid_batch_never_changes_any_row(self):
        bad_batches = [(Mark(2, 'present'),),
                       (Mark(2, 'present'), Mark(2, 'absent')),
                       (Mark(2, 'present'), Mark(4, 'absent')),
                       (Mark(2, 'present'), Mark(3, None)),
                       (Mark(2, 'present'), Mark(3, 'unknown')),
                       (Mark(True, 'present'), Mark(3, 'absent'))]
        initial = self.store.load(42)
        for marks in bad_batches:
            with self.subTest(marks=marks):
                with self.assertRaises(InvalidInput):
                    self.service.save(self.teacher, 42, 0, marks)
                self.assertEqual(self.store.load(42), initial)

    def test_revision_bool_is_not_an_integer_revision(self):
        with self.assertRaises(InvalidInput):
            self.service.save(self.teacher, 42, True, self.marks)

    def test_compare_and_set_rejects_second_snapshot(self):
        # Two preloaded snapshots, then two writes. Not a parallel load test.
        snapshot_a = self.store.load(42)
        snapshot_b = self.store.load(42)
        first = replace(snapshot_a, revision=1, marks=self.marks)
        second = replace(snapshot_b, revision=1,
                         marks=(Mark(2, 'late'), Mark(3, 'absent')))
        self.assertTrue(self.store.replace(0, first))
        self.assertFalse(self.store.replace(0, second))
        self.assertEqual(self.store.load(42), first)

    def test_service_rechecks_when_compare_and_set_loses(self):
        outer = self
        for same in (True, False):
            with self.subTest(same=same):
                engine = make_lab_engine()
                try:
                    seed_demo(engine)
                    actual = SqlStore(engine)
                    class CompetingStore:
                        def load(self, sheet_id):
                            return actual.load(sheet_id)
                        def replace(self, expected, next_sheet):
                            marks = outer.marks if same else (
                                Mark(2, 'late'), Mark(3, 'absent'))
                            actual.replace(expected, replace(next_sheet, marks=marks))
                            return False
                    service = AttendanceService(CompetingStore())
                    if same:
                        self.assertEqual(service.save(self.teacher, 42, 0, self.marks).revision, 1)
                    else:
                        with self.assertRaises(Conflict):
                            service.save(self.teacher, 42, 0, self.marks)
                finally:
                    engine.dispose()

    def test_db_exception_rolls_back_guard_and_earlier_marks(self):
        initial = self.store.load(42)
        # Bypass service deliberately: adapter must also preserve transaction atomicity.
        broken = replace(initial, revision=1,
                         marks=(Mark(2, 'present'), Mark(3, 'illegal')))
        with self.assertRaises(IntegrityError):
            self.store.replace(0, broken)
        self.assertEqual(self.store.load(42), initial)

    def test_primary_key_rejects_duplicate_student(self):
        with self.assertRaises(IntegrityError):
            with self.store.sessions.begin() as db:
                db.add(MarkRow(sheet_id=42, student_id=2, status='present'))
        with self.store.sessions() as db:
            self.assertEqual(len(db.scalars(select(MarkRow)).all()), 2)

    def test_foreign_key_rejects_mark_for_missing_sheet(self):
        with self.assertRaises(IntegrityError):
            with self.store.sessions.begin() as db:
                db.add(MarkRow(sheet_id=999, student_id=2, status='present'))


if __name__ == '__main__':
    unittest.main()
