"""SQLAlchemy adapter. These tables belong only to this isolated teaching lab."""
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, create_engine, event, select, update
from sqlalchemy.orm import declarative_base, sessionmaker
from core import Mark, Sheet


Base = declarative_base()


def make_lab_engine():
    engine = create_engine('sqlite://')
    @event.listens_for(engine, 'connect')
    def enable_foreign_keys(connection, _record):
        connection.execute('PRAGMA foreign_keys=ON')
    return engine


class SheetRow(Base):
    __tablename__ = 'attendance_sheets'
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, nullable=False)
    teacher_id = Column(Integer, nullable=False)
    revision = Column(Integer, nullable=False, default=0)
    __table_args__ = (CheckConstraint('revision >= 0', name='ck_revision'),)


class MarkRow(Base):
    __tablename__ = 'attendance_marks'
    sheet_id = Column(Integer, ForeignKey('attendance_sheets.id'), primary_key=True)
    student_id = Column(Integer, primary_key=True)
    status = Column(String(20), nullable=True)
    __table_args__ = (CheckConstraint(
        "status IS NULL OR status IN ('present', 'late', 'absent', 'excused')",
        name='ck_attendance_status'),)


class SqlStore:
    def __init__(self, engine):
        self.sessions = sessionmaker(bind=engine, expire_on_commit=False)

    def load(self, sheet_id):
        # One SELECT avoids reading revision in one snapshot and marks in another.
        query = select(SheetRow.id, SheetRow.class_id, SheetRow.teacher_id,
                       SheetRow.revision, MarkRow.student_id, MarkRow.status).outerjoin(
            MarkRow, MarkRow.sheet_id == SheetRow.id).where(
            SheetRow.id == sheet_id).order_by(MarkRow.student_id)
        with self.sessions() as db:
            rows = db.execute(query).all()
        if not rows:
            return None
        first = rows[0]
        return Sheet(first.id, first.class_id, first.teacher_id, first.revision,
                     tuple(Mark(row.student_id, row.status) for row in rows
                           if row.student_id is not None))

    def replace(self, expected_revision, next_sheet):
        # The guarded UPDATE and every mark update share ONE transaction.
        with self.sessions.begin() as db:
            changed = db.execute(update(SheetRow).where(
                SheetRow.id == next_sheet.id,
                SheetRow.revision == expected_revision).values(
                revision=next_sheet.revision)).rowcount
            if changed != 1:
                return False
            for mark in next_sheet.marks:
                result = db.execute(update(MarkRow).where(
                    MarkRow.sheet_id == next_sheet.id,
                    MarkRow.student_id == mark.student_id).values(status=mark.status))
                if result.rowcount != 1:
                    raise RuntimeError('Roster changed; roll back the whole sheet')
        return True


def seed_demo(engine):
    """Fixed snapshot, not a real membership/calendar/auth implementation."""
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    with sessions.begin() as db:
        db.add(SheetRow(id=42, class_id=7, teacher_id=1, revision=0))
        db.flush()
        db.add_all([MarkRow(sheet_id=42, student_id=2, status=None),
                    MarkRow(sheet_id=42, student_id=3, status=None)])
