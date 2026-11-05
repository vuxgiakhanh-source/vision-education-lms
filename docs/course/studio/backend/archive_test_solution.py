"""Copy as test_archive.py into the disposable patched workshop, never the product."""
import unittest
from sqlalchemy import select
import test_workshop as support
from lms_lab.models import Assignment, Classroom, Membership, Submission, User
from lms_lab.repository import ClassRepository
from lms_lab.service import ClassService


class ArchiveTests(unittest.TestCase):
    setUp = support.WorkshopTests.setUp
    tearDown = support.WorkshopTests.tearDown
    call = support.WorkshopTests.call

    def assignment(self):
        status, row = self.call('POST', '/classes/1/assignments', body={'title': 'Bài cũ'})
        self.assertEqual(status, 201)
        return row['id']

    def test_archive_checks_identity_and_owner_before_writing(self):
        path = '/classes/1/archive'
        self.assertEqual(self.call('PUT', path, user=None)[0], 401)
        self.assertEqual(self.call('PUT', path, user=2)[0], 403)
        with self.sessions() as db:
            db.add(User(id=5, name='Other', role='teacher'))
            db.commit()
        self.assertEqual(self.call('PUT', path, user=5)[0], 404)
        self.assertEqual(self.call('PUT', '/classes/999/archive')[0], 404)
        with self.sessions() as db:
            self.assertFalse(db.get(Classroom, 1).archived)

    def test_archive_preserves_history_and_repeating_is_safe(self):
        assignment_id = self.assignment()
        first = self.call('PUT', '/classes/1/archive')
        self.assertEqual(first[0], 200)
        self.assertTrue(first[1]['archived'])
        self.assertEqual(self.call('PUT', '/classes/1/archive'), first)
        self.assertEqual(self.call('GET', '/classes/1', user=2)[0], 200)
        self.assertEqual(self.call('GET', '/classes/1/assignments', user=2)[1][0]['id'], assignment_id)
        self.assertEqual(self.call('GET', '/classes/1', user=3)[0], 404)
        with self.sessions() as db:
            self.assertIsNotNone(db.get(Assignment, assignment_id))
            self.assertEqual(len(db.scalars(select(Membership)).all()), 1)

    def test_archived_class_blocks_new_assignment_and_submission(self):
        assignment_id = self.assignment()
        self.call('PUT', '/classes/1/archive')
        self.assertEqual(self.call('POST', '/classes/1/assignments', body={'title': 'Không tạo'})[0], 409)
        self.assertEqual(self.call('POST', f'/assignments/{assignment_id}/submissions', user=2,
                                   body={'answer': 'Không nộp mới'})[0], 409)
        with self.sessions() as db:
            self.assertEqual(len(db.scalars(select(Assignment)).all()), 1)
            self.assertEqual(db.scalars(select(Submission)).all(), [])

    def test_existing_retry_and_grading_work_after_archive(self):
        assignment_id = self.assignment()
        path = f'/assignments/{assignment_id}/submissions'
        first = self.call('POST', path, user=2, body={'answer': 'A'})
        self.call('PUT', '/classes/1/archive')
        self.assertEqual(self.call('POST', path, user=2, body={'answer': ' A '}), first)
        self.assertEqual(self.call('POST', path, user=2, body={'answer': 'B'})[0], 409)
        grade = f'/submissions/{first[1]["id"]}/grade'
        self.assertEqual(self.call('PUT', grade, body={'score': 0, 'publish': True})[0], 200)
        status, mine = self.call('GET', f'/assignments/{assignment_id}/my-submission', user=2)
        self.assertEqual(status, 200)
        self.assertEqual(mine['score'], 0)
        with self.sessions() as db:
            self.assertEqual(len(db.scalars(select(Submission)).all()), 1)

    def test_client_cannot_archive_through_title_input(self):
        self.assertEqual(self.call('PATCH', '/classes/1', body={'title': 'X', 'archived': True})[0], 422)
        with self.sessions() as db:
            self.assertFalse(db.get(Classroom, 1).archived)
            self.assertEqual(db.get(Classroom, 1).title, 'Algebra')

    def test_failure_during_commit_rolls_back_archived_flag(self):
        with self.sessions() as db:
            class FailingTransaction:
                def commit(self):
                    db.flush()
                    raise RuntimeError('Injected failure after flush')

                def rollback(self):
                    db.rollback()

            service = ClassService(ClassRepository(db), FailingTransaction())
            with self.assertRaises(RuntimeError):
                service.archive(db.get(User, 1), 1)
        with self.sessions() as fresh:
            self.assertFalse(fresh.get(Classroom, 1).archived)


if __name__ == '__main__':
    unittest.main()
