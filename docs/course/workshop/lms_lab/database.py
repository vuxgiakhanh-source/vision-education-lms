from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def make_engine(url: str, **pool_options):
    options = {'connect_args': {'check_same_thread': False}} if url.startswith('sqlite:') else pool_options
    if url in {'sqlite://', 'sqlite:///:memory:'}:
        options['poolclass'] = StaticPool
    engine = create_engine(url, **options)
    if url.startswith('sqlite:'):
        @event.listens_for(engine, 'connect')
        def enable_foreign_keys(connection, _record):
            cursor = connection.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.close()
    return engine


def session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
