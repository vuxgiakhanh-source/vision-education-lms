"""Print short-lived, local lab credentials, never include output in the book."""
from datetime import datetime, timedelta, timezone
import json
import os
from jose import jwt
from sqlalchemy import select
from lms_lab.server import engine
from lms_lab.database import session_factory
from lms_lab.models import User

if engine.url.database != 'lms_lab':
    raise SystemExit('Chỉ xuất fixture lms_lab')
with session_factory(engine)() as db:
    ids = db.scalars(select(User.id).where(User.role == 'student', User.active == 1, User.id != 3).order_by(User.id)).all()
expiry = datetime.now(timezone.utc) + timedelta(hours=2)
print(json.dumps([{'student_id': id, 'token': jwt.encode({'sub': str(id), 'exp': expiry},
                  os.environ['LAB_SECRET'], algorithm='HS256')} for id in ids]))
