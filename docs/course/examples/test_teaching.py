"""Check authored teaching examples; SQLite tests do not stand in for MySQL."""
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from sqlalchemy import Column, ForeignKey, Integer, create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker

EXAMPLES = json.loads((Path(__file__).parent.parent / 'teaching-content.json').read_text(encoding='utf-8'))['examples']


def load_function(lesson, name):
    namespace = {}
    exec(compile(EXAMPLES[lesson]['code'], f'teaching-content:{lesson}', 'exec'), namespace)
    return namespace[name]


class TeachingExamplesTests(unittest.TestCase):
    def test_average_keeps_zero_and_input(self):
        average = load_function('python', 'average_graded')
        scores = [0, None, 10]
        self.assertEqual(average(scores), 5)
        self.assertEqual(scores, [0, None, 10])
        self.assertEqual(average([0]), 0)
        self.assertIsNone(average([None]))
        self.assertIsNone(average([]))

    def test_name_service_uses_reader_contract(self):
        service_type = load_function('05', 'NameService')
        calls = []

        class Reader:
            def find(self, user_id):
                calls.append(user_id)
                return SimpleNamespace(name='An') if user_id == 2 else None

        service = service_type(Reader())
        self.assertEqual(service.label(2), 'An')
        self.assertIsNone(service.label(99))
        self.assertEqual(calls, [2, 99])

    def check_transaction(self, fail):
        base = declarative_base()

        class Classroom(base):
            __tablename__ = 'classes'
            id = Column(Integer, primary_key=True)

        class Membership(base):
            __tablename__ = 'memberships'
            id = Column(Integer, primary_key=True)
            class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
            student_id = Column(Integer, nullable=False)

        engine = create_engine('sqlite:///:memory:')
        try:
            base.metadata.create_all(engine)
            sessions = sessionmaker(bind=engine)
            save = load_function('08', 'save_pair')
            with sessions() as db:
                classroom = Classroom()
                membership = Membership(student_id=None if fail else 2)
                if fail:
                    with self.assertRaises(IntegrityError):
                        save(db, classroom, membership)
                else:
                    save(db, classroom, membership)
            with sessions() as fresh:
                expected = 0 if fail else 1
                self.assertEqual(fresh.scalar(select(func.count()).select_from(Classroom)), expected)
                self.assertEqual(fresh.scalar(select(func.count()).select_from(Membership)), expected)
        finally:
            engine.dispose()

    def test_pair_commits_both(self):
        self.check_transaction(False)

    def test_pair_rolls_back_after_first_flush(self):
        self.check_transaction(True)


if __name__ == '__main__':
    unittest.main()
