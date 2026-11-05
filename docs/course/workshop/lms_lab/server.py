"""Container lab entry point; distinct from the fixture CLI and product app."""
import json
import logging
import os
from time import perf_counter
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import URL, text
from .app import create_app
from .database import make_engine

url = URL.create('mysql+pymysql', username=os.environ['LAB_DB_USER'],
                 password=os.environ['LAB_DB_PASSWORD'], host=os.environ.get('LAB_DB_HOST', 'db'),
                 database=os.environ.get('LAB_DB_NAME', 'lms_lab'))
engine = make_engine(url.render_as_string(hide_password=False), pool_pre_ping=True,
                     pool_size=int(os.environ.get('LAB_POOL_SIZE', '5')),
                     max_overflow=int(os.environ.get('LAB_MAX_OVERFLOW', '5')),
                     pool_timeout=3, connect_args={'connect_timeout': 3, 'read_timeout': 5, 'write_timeout': 5})
app = create_app(engine, os.environ['LAB_SECRET'])
logger = logging.getLogger('uvicorn.error')


@app.get('/ready')
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))
    except Exception:
        raise HTTPException(503, 'Database chưa sẵn sàng') from None
    return {'status': 'ready'}


@app.middleware('http')
async def request_log(request, call_next):
    request_id, started, status = uuid4().hex, perf_counter(), 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers['X-Request-ID'] = request_id
        return response
    finally:
        route = request.scope.get('route')
        logger.info(json.dumps({'request_id': request_id, 'method': request.method,
                    'route': getattr(route, 'path', 'unmatched'), 'status': status,
                    'elapsed_ms': round((perf_counter() - started) * 1000, 2)}))
