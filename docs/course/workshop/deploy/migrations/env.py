import os
from alembic import context
from sqlalchemy import URL, create_engine, pool
from lms_lab.models import Base

# Tests may set a disposable URL programmatically; normal container runs use env.
test_connection = context.config.attributes.get('test_connection')
url = context.config.attributes.get('test_url')
if url is None and test_connection is None:
    url = URL.create('mysql+pymysql', username=os.environ['LAB_DB_USER'],
                     password=os.environ['LAB_DB_PASSWORD'], host=os.environ.get('LAB_DB_HOST', 'db'),
                     database=os.environ.get('LAB_DB_NAME', 'lms_lab'))
if test_connection is not None:
    context.configure(connection=test_connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
elif context.is_offline_mode():
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with create_engine(url, poolclass=pool.NullPool).connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()
