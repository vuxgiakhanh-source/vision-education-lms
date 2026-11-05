"""Run reviewed baseline against disposable SQLite, compare ORM metadata."""
from pathlib import Path
import unittest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect
from lms_lab.database import make_engine
from lms_lab.models import Base


class MigrationTests(unittest.TestCase):
    def test_baseline_upgrade_matches_models_and_downgrade(self):
        root = Path(__file__).parent / 'deploy'
        engine = make_engine('sqlite://')
        try:
            with engine.connect() as connection:
                config = Config(str(root / 'alembic.ini'))
                config.attributes['test_connection'] = connection
                command.upgrade(config, 'head')
                self.assertEqual(compare_metadata(MigrationContext.configure(connection), Base.metadata), [])
                self.assertIn('submissions', inspect(connection).get_table_names())
                command.downgrade(config, 'base')
                self.assertEqual(set(inspect(connection).get_table_names()), {'alembic_version'})
        finally:
            engine.dispose()
