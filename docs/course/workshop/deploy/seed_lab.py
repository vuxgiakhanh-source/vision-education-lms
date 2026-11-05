"""Seed only an EMPTY lms_lab database after Alembic, never reset existing data."""
import argparse
from sqlalchemy import func, select
from lms_lab.server import engine
from lms_lab.database import session_factory
from lms_lab.models import Assignment, Classroom, Membership, User

parser = argparse.ArgumentParser()
parser.add_argument('--students', type=int, default=200)
parser.add_argument('--assignments', type=int, default=1000)
args = parser.parse_args()
if engine.url.database != 'lms_lab' or not 2 <= args.students <= 5000 or not 1 <= args.assignments <= 10000:
    parser.error('Chỉ DB lms_lab; students 2..5000, assignments 1..10000')
with session_factory(engine)() as db:
    if db.scalar(select(func.count()).select_from(User)):
        parser.error('DB không rỗng; không seed/reset/ghi đè')
    db.add_all([User(id=1, name='Teacher fixture', role='teacher'),
                User(id=3, name='Outsider fixture', role='student'),
                User(id=4, name='Locked fixture', role='student', active=0)])
    student_ids = [2] + list(range(5, args.students + 4))
    db.add_all([User(id=user_id, name=f'Student {user_id}', role='student') for user_id in student_ids])
    db.flush()
    db.add(Classroom(id=1, title='Load lab', teacher_id=1))
    db.flush()
    db.add_all([Membership(class_id=1, student_id=user_id) for user_id in student_ids])
    db.add_all([Assignment(id=i, class_id=1, title=f'Assignment {i}') for i in range(1, args.assignments + 1)])
    db.commit()
print(f'Fixture committed: {args.students} students, {args.assignments} assignments; no submissions yet.')
