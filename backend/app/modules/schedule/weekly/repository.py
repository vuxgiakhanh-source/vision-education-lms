from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import Row, select
from sqlalchemy.orm import Session

from app.models.classroom import Class
from app.models.schedule import ClassSession


class WeeklyScheduleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_sessions_in_range(
        self,
        grade: int,
        starts_from: datetime,
        starts_before: datetime,
    ) -> Sequence[Row]:
        statement = (
            select(
                ClassSession.id,
                ClassSession.class_id,
                Class.name.label("class_name"),
                ClassSession.teaching_week,
                ClassSession.topic,
                ClassSession.starts_at,
                ClassSession.ends_at,
            )
            .join(Class, ClassSession.class_id == Class.id)
            .where(
                Class.grade == grade,
                ClassSession.starts_at >= starts_from,
                ClassSession.starts_at < starts_before,
                ClassSession.status == "scheduled",
            )
            .order_by(ClassSession.starts_at, ClassSession.id)
        )
        return self.db.execute(statement).all()
