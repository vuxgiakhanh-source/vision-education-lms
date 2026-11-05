"""Core acceptance matrix. In-memory SQLite/ASGI, not MySQL locking proof."""
from datetime import datetime
import unittest
from sqlalchemy import select
import test_workshop as support
from lms_lab.models import Assignment, Classroom, Submission, User
from lms_lab.unit_of_work import SqlTransaction
from lms_lab.workflow import WorkflowRepository, WorkflowService


class WorkflowTests(unittest.TestCase):
    setUp = support.WorkshopTests.setUp
    tearDown = support.WorkshopTests.tearDown
    call = support.WorkshopTests.call

    def assignment(self, due_at=None):
        status, row = self.call('POST', '/classes/1/assignments', body={'title': '  Bài 1  ', 'due_at': due_at})
        self.assertEqual(status, 201)
        self.assertEqual(row['title'], 'Bài 1')
        return row['id']

    def submit(self, assignment, answer=' A '):
        return self.call('POST', f'/assignments/{assignment}/submissions', user=2, body={'answer': answer})

    def test_complete_loop_hidden_zero_then_published(self):
        assignment = self.assignment()
        status, row = self.submit(assignment)
        self.assertEqual(status, 200)
        self.assertEqual(row['answer'], 'A')
        path = f'/submissions/{row["id"]}/grade'
        self.assertEqual(self.call('PUT', path, body={'score': 0, 'publish': False})[0], 200)
        mine = f'/assignments/{assignment}/my-submission'
        self.assertIsNone(self.call('GET', mine, user=2)[1]['score'])
        teacher = self.call('GET', f'/assignments/{assignment}/submissions')[1]
        self.assertEqual(teacher[0]['score'], 0)
        self.assertEqual(self.call('PUT', path, body={'score': 0, 'publish': True})[0], 200)
        self.assertEqual(self.call('GET', mine, user=2)[1]['score'], 0)
        with self.sessions() as db:
            saved = db.get(Submission, row['id'])
            self.assertEqual(saved.score, 0)
            self.assertTrue(saved.grade_published)

    def test_same_retry_preserves_original(self):
        assignment = self.assignment()
        first = self.submit(assignment)[1]
        self.assertEqual(self.submit(assignment, 'A')[1], first)
        self.assertEqual(self.submit(assignment, 'B')[0], 409)
        with self.sessions() as db:
            rows = db.scalars(select(Submission)).all()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].answer, 'A')

    def test_deadline_and_retry_after_deadline(self):
        assignment = self.assignment('2000-01-01T00:00:00Z')
        self.assertEqual(self.submit(assignment)[0], 409)
        with self.sessions() as db:
            self.assertEqual(db.scalars(select(Submission)).all(), [])
        assignment = self.assignment()
        first = self.submit(assignment)[1]
        with self.sessions() as db:
            db.get(Assignment, assignment).due_at = datetime(2000, 1, 1)
            db.commit()
        self.assertEqual(self.submit(assignment)[1], first)

    def test_scope_every_read_and_write(self):
        assignment = self.assignment()
        row = self.submit(assignment)[1]
        for path in ['/classes/1/assignments', f'/assignments/{assignment}/my-submission']:
            self.assertEqual(self.call('GET', path, user=3)[0], 404)
        self.assertEqual(self.call('POST', f'/assignments/{assignment}/submissions', user=3, body={'answer': 'X'})[0], 404)
        self.assertEqual(self.call('GET', f'/assignments/{assignment}/submissions', user=2)[0], 403)
        self.assertEqual(self.call('PUT', f'/submissions/{row["id"]}/grade', user=2, body={'score': 10, 'publish': True})[0], 403)
        self.assertEqual(self.call('POST', '/classes/1/assignments', user=2, body={'title': 'X'})[0], 403)

    def test_other_teacher_and_nested_resource(self):
        assignment = self.assignment()
        row = self.submit(assignment)[1]
        with self.sessions() as db:
            db.add(User(id=5, name='Other teacher', role='teacher'))
            db.flush()
            db.add(Classroom(id=2, title='Other', teacher_id=5))
            db.commit()
        self.assertEqual(self.call('GET', '/classes/2/assignments')[0], 404)
        self.assertEqual(self.call('GET', f'/assignments/{assignment}/submissions', user=5)[0], 404)
        self.assertEqual(self.call('PUT', f'/submissions/{row["id"]}/grade', user=5, body={'score': 9, 'publish': True})[0], 404)

    def test_schema_deadline_and_pagination(self):
        for payload in [{'title': ' '}, {'title': 'X', 'teacher_id': 2},
                        {'title': 'X', 'due_at': '2030-01-01T12:00:00'}]:
            self.assertEqual(self.call('POST', '/classes/1/assignments', body=payload)[0], 422)
        assignment = self.assignment('2030-01-01T12:00:00+07:00')
        item = self.call('GET', '/classes/1/assignments')[1][0]
        self.assertTrue(item['due_at'].startswith('2030-01-01T05:00:00'))
        self.assertEqual(self.call('GET', '/classes/1/assignments', query='page_size=101')[0], 422)
        for payload in [{'answer': ''}, {'answer': 'x' * 2001}, {'answer': 'A', 'score': 10}]:
            self.assertEqual(self.call('POST', f'/assignments/{assignment}/submissions', user=2, body=payload)[0], 422)

    def test_grade_validation_and_withdraw(self):
        row = self.submit(self.assignment())[1]
        path = f'/submissions/{row["id"]}/grade'
        for score in [-1, 11, True, 2.5, '5']:
            self.assertEqual(self.call('PUT', path, body={'score': score, 'publish': True})[0], 422)
        self.call('PUT', path, body={'score': 7, 'publish': True})
        self.call('PUT', path, body={'score': 8, 'publish': False})
        mine = self.call('GET', f'/assignments/{row["assignment_id"]}/my-submission', user=2)[1]
        self.assertIsNone(mine['score'])
        self.assertFalse(mine['grade_published'])

    def test_failure_after_flush_rolls_back_submission(self):
        assignment = self.assignment()
        class FailingRepository(WorkflowRepository):
            def add(self, row):
                super().add(row)
                raise RuntimeError('Injected failure after INSERT')
        with self.sessions() as db:
            actor = db.get(User, 2)
            flow = WorkflowService(FailingRepository(db), SqlTransaction(db))
            with self.assertRaises(RuntimeError):
                flow.submit(actor, assignment, 'A')
        with self.sessions() as db:
            self.assertEqual(db.scalars(select(Submission)).all(), [])


if __name__ == '__main__':
    unittest.main()
