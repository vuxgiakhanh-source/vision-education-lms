"""ASGI + SQLite integration checks; no httpx/network/product DB required."""
import asyncio
from datetime import datetime, timedelta, timezone
import json
import unittest
from jose import jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from lms_lab.app import create_app
from lms_lab.database import make_engine, session_factory
from lms_lab.models import Base, Classroom, Membership, User
from lms_lab.repository import ClassRepository
from lms_lab.service import ClassService
from lms_lab.unit_of_work import SqlTransaction

SECRET = 'test-only-key-which-is-never-used-outside-disposable-tests'


async def request(app, method, path, token=None, body=None, query=''):
    raw = json.dumps(body).encode() if body is not None else b''
    headers = [(b'content-type', b'application/json')]
    if token:
        headers.append((b'authorization', ('Bearer ' + token).encode()))
    scope = {'type': 'http', 'asgi': {'version': '3.0'}, 'http_version': '1.1',
             'method': method, 'scheme': 'http', 'path': path, 'raw_path': path.encode(),
             'query_string': query.encode(), 'root_path': '', 'headers': headers,
             'server': ('test', 80), 'client': ('test', 1)}
    messages = []

    async def receive():
        return {'type': 'http.request', 'body': raw, 'more_body': False}

    async def send(message):
        messages.append(message)

    await app(scope, receive, send)
    status = next(m['status'] for m in messages if m['type'] == 'http.response.start')
    content = b''.join(m.get('body', b'') for m in messages if m['type'] == 'http.response.body')
    return status, json.loads(content) if content else None


class WorkshopTests(unittest.TestCase):
    def setUp(self):
        self.engine = make_engine('sqlite://')
        Base.metadata.create_all(self.engine)
        self.sessions = session_factory(self.engine)
        with self.sessions() as db:
            db.add_all([User(id=1, name='Teacher', role='teacher'),
                        User(id=2, name='Member', role='student'),
                        User(id=3, name='Other', role='student'),
                        User(id=4, name='Locked', role='student', active=0)])
            db.flush()
            db.add(Classroom(id=1, title='Algebra', teacher_id=1))
            db.flush()
            db.add(Membership(class_id=1, student_id=2))
            db.commit()
        self.app = create_app(self.engine, SECRET)

    def tearDown(self):
        self.engine.dispose()

    def call(self, method, path, user=1, body=None, query='', token=None):
        if token is None and user is not None:
            token = jwt.encode({'sub': str(user), 'exp': datetime.now(timezone.utc) + timedelta(minutes=5)}, SECRET, algorithm='HS256')
        return asyncio.run(request(self.app, method, path, token, body, query))

    def test_missing_auth(self):
        self.assertEqual(self.call('GET', '/classes', user=None)[0], 401)

    def test_invalid_signature(self):
        token = jwt.encode({'sub': '1', 'exp': datetime.now(timezone.utc) + timedelta(minutes=5)}, SECRET + 'wrong', algorithm='HS256')
        self.assertEqual(self.call('GET', '/classes', token=token)[0], 401)

    def test_expired_and_missing_exp(self):
        expired = jwt.encode({'sub': '1', 'exp': datetime.now(timezone.utc) - timedelta(minutes=1)}, SECRET, algorithm='HS256')
        missing = jwt.encode({'sub': '1'}, SECRET, algorithm='HS256')
        for token in [expired, missing]:
            self.assertEqual(self.call('GET', '/classes', token=token)[0], 401)

    def test_locked_and_unknown_user(self):
        self.assertEqual(self.call('GET', '/classes', user=4)[0], 403)
        self.assertEqual(self.call('GET', '/classes', user=99)[0], 401)

    def test_teacher_creates_and_trim_persists(self):
        status, data = self.call('POST', '/classes', body={'title': '  Calculus  '})
        self.assertEqual(status, 201)
        self.assertEqual(data['title'], 'Calculus')
        with self.sessions() as db:
            self.assertEqual(db.get(Classroom, data['id']).teacher_id, 1)

    def test_student_cannot_create(self):
        self.assertEqual(self.call('POST', '/classes', user=2, body={'title': 'X'})[0], 403)
        with self.sessions() as db:
            self.assertEqual(len(list(db.scalars(select(Classroom)))), 1)

    def test_schema_rejects_empty_missing_long_and_extra(self):
        for body in [{}, {'title': '   '}, {'title': None}, {'title': 'a' * 201}, {'title': '😀' * 201}, {'title': 'X', 'teacher_id': 2}]:
            self.assertEqual(self.call('POST', '/classes', body=body)[0], 422)

    def test_unicode_title_limit(self):
        title = '😀' * 200
        status, data = self.call('POST', '/classes', body={'title': title})
        self.assertEqual(status, 201)
        self.assertEqual(data['title'], title)

    def test_lists_filter_by_actor(self):
        self.assertEqual(len(self.call('GET', '/classes', user=1)[1]), 1)
        self.assertEqual(len(self.call('GET', '/classes', user=2)[1]), 1)
        self.assertEqual(self.call('GET', '/classes', user=3)[1], [])

    def test_detail_and_missing_scope(self):
        self.assertEqual(self.call('GET', '/classes/1', user=2)[0], 200)
        self.assertEqual(self.call('GET', '/classes/1', user=3)[0], 404)
        self.assertEqual(self.call('GET', '/classes/999')[0], 404)

    def test_rename_checks_owner_and_persists(self):
        self.assertEqual(self.call('PATCH', '/classes/1', user=2, body={'title': 'Hacked'})[0], 403)
        self.assertEqual(self.call('PATCH', '/classes/1', user=3, body={'title': 'Hacked'})[0], 404)
        self.assertEqual(self.call('PATCH', '/classes/1', body={'title': '  Renamed '})[1]['title'], 'Renamed')
        self.assertEqual(self.call('GET', '/classes/1', user=2)[1]['title'], 'Renamed')

    def test_pagination_validation_and_page(self):
        self.assertEqual(self.call('GET', '/classes', query='page=0')[0], 422)
        self.assertEqual(self.call('GET', '/classes', query='page_size=101')[0], 422)
        self.assertEqual(self.call('GET', '/classes', query='page=2&page_size=1')[1], [])

    def test_positive_id(self):
        self.assertEqual(self.call('GET', '/classes/0')[0], 422)

    def test_other_teacher_scope(self):
        with self.sessions() as db:
            db.add(User(id=5, name='Other teacher', role='teacher'))
            db.commit()
        self.assertEqual(self.call('GET', '/classes', user=5)[1], [])
        self.assertEqual(self.call('GET', '/classes/1', user=5)[0], 404)
        self.assertEqual(self.call('PATCH', '/classes/1', user=5, body={'title': 'X'})[0], 404)

    def test_unique_membership(self):
        with self.sessions() as db:
            db.add(Membership(class_id=1, student_id=2))
            with self.assertRaises(IntegrityError):
                db.commit()
            db.rollback()
            self.assertEqual(len(list(db.scalars(select(Membership)))), 1)

    def test_foreign_key(self):
        with self.sessions() as db:
            db.add(Membership(class_id=999, student_id=2))
            with self.assertRaises(IntegrityError):
                db.commit()
            db.rollback()

    def test_service_rolls_back_after_flush_error(self):
        class FailingRepository(ClassRepository):
            def add(self, classroom):
                super().add(classroom)
                raise RuntimeError('Injected failure after flush')
        with self.sessions() as db:
            service = ClassService(FailingRepository(db), SqlTransaction(db))
            with self.assertRaises(RuntimeError):
                service.create(db.get(User, 1), 'Should roll back')
        with self.sessions() as fresh:
            self.assertEqual(len(list(fresh.scalars(select(Classroom)))), 1)


if __name__ == '__main__':
    unittest.main()
