"""Upgrade an existing baseline row, not just an empty create_all database."""
from pathlib import Path
import unittest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from lms_lab.database import make_engine


class ArchiveMigrationTests(unittest.TestCase):
    def test_existing_class_gets_false_default_without_losing_title(self):
        engine = make_engine('sqlite://')
        try:
            with engine.connect() as connection:
                config = Config(str(Path(__file__).parent / 'deploy' / 'alembic.ini'))
                config.attributes['test_connection'] = connection
                command.upgrade(config, '0001')
                connection.execute(text("INSERT INTO users(id,name,role,active) VALUES (1,'Cô','teacher',1)"))
                connection.execute(text("INSERT INTO classes(id,title,teacher_id) VALUES (1,'Lớp cũ',1)"))
                connection.commit()
                command.upgrade(config, 'head')
                row = connection.execute(text('SELECT title, archived FROM classes WHERE id=1')).one()
                self.assertEqual(tuple(row), ('Lớp cũ', 0))
        finally:
            engine.dispose()


if __name__ == '__main__':
    unittest.main()
