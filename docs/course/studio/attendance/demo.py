"""Run from the course attendance directory or by absolute script path."""
from core import Actor, AttendanceService, Conflict, Mark
from storage import SqlStore, make_lab_engine, seed_demo


engine = make_lab_engine()
seed_demo(engine)
service = AttendanceService(SqlStore(engine))
teacher = Actor(1, 'teacher')
marks = (Mark(2, 'present'), Mark(3, 'absent'))
saved = service.save(teacher, 42, 0, marks)
retried = service.save(teacher, 42, 0, marks)
print('saved revision:', saved.revision)
print('retry revision:', retried.revision)
try:
    service.save(teacher, 42, 0, (Mark(2, 'late'), Mark(3, 'absent')))
except Conflict:
    print('stale different content: conflict')
print('stored marks:', service.read(teacher, 42).marks)
