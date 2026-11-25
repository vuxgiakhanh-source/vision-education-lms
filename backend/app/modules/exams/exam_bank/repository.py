from collections.abc import Sequence

from sqlalchemy import Row, select
from sqlalchemy.orm import Session

from app.models.exam import ExamPaper


class ExamBankRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_owned_choices(self, teacher_id: int) -> Sequence[Row[int, str]]:
        return self.db.execute(
            select(ExamPaper.id, ExamPaper.title)
            .where(ExamPaper.created_by == teacher_id)
            .order_by(ExamPaper.title, ExamPaper.id)
        ).all()

    def get_owned_paper_id(self, paper_id: int, teacher_id: int) -> int | None:
        # Giữ quyền sở hữu và sự tồn tại của đề ổn định đến khi giao dịch của luồng gọi kết thúc.
        statement = (
            select(ExamPaper.id)
            .where(ExamPaper.id == paper_id, ExamPaper.created_by == teacher_id)
            .with_for_update(read=True)
        )
        return self.db.scalar(statement)
