"""Opt-in MySQL locking check. Requires an EMPTY disposable lms_concurrency_* DB."""
from concurrent.futures import ThreadPoolExecutor
import os
from threading import Barrier
import unittest
from sqlalchemy import func, inspect, select
from lms_lab.database import make_engine, session_factory
from lms_lab.models import Assignment, Base, Classroom, Membership, Submission, User
from lms_lab.unit_of_work import SqlTransaction
from lms_lab.workflow import Conflict, WorkflowRepository, WorkflowService


@unittest.skipUnless(os.environ.get('LAB_MYSQL_TEST_URL'), 'Chưa cấp URL database MySQL học riêng')
class MysqlConcurrencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = make_engine(os.environ['LAB_MYSQL_TEST_URL'])
        if cls.engine.dialect.name != 'mysql' or not (cls.engine.url.database or '').startswith('lms_concurrency_'):
            cls.engine.dispose()
            raise RuntimeError('Chỉ dùng database MySQL mới tên lms_concurrency_*')
        if inspect(cls.engine).get_table_names():
            cls.engine.dispose()
            raise RuntimeError('DB không rỗng; không tự reset/xóa dữ liệu')
        Base.metadata.create_all(cls.engine)
        cls.sessions = session_factory(cls.engine)
        with cls.sessions() as db:
            db.add_all([User(id=1, name='Teacher', role='teacher'), User(id=2, name='Student', role='student')])
            db.flush()
            db.add(Classroom(id=1, title='Concurrency', teacher_id=1))
            db.flush()
            db.add_all([Membership(class_id=1, student_id=2), Assignment(id=1, class_id=1, title='Same retry'),
                        Assignment(id=2, class_id=1, title='Different answers')])
            db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()  # Leave lab evidence; never drop the database automatically.

    def race(self, assignment_id, answers):
        barrier = Barrier(2)
        def submit(answer):
            with self.sessions() as db:
                actor = db.get(User, 2)
                barrier.wait(timeout=10)
                try:
                    return WorkflowService(WorkflowRepository(db), SqlTransaction(db)).submit(actor, assignment_id, answer)
                except Conflict:
                    return 'conflict'
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(submit, answer) for answer in answers]
            result = [future.result(timeout=30) for future in futures]
        with self.sessions() as db:
            count = db.scalar(select(func.count()).select_from(Submission).where(Submission.assignment_id == assignment_id))
            self.assertEqual(count, 1)
        return result

    def test_same_content_has_one_id_and_timestamp(self):
        first, second = self.race(1, ['A', 'A'])
        self.assertEqual(first['id'], second['id'])
        self.assertEqual(first['submitted_at'], second['submitted_at'])

    def test_different_content_has_one_winner(self):
        result = self.race(2, ['A', 'B'])
        self.assertEqual(result.count('conflict'), 1)
