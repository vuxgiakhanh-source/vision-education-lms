"""Allow incomplete exam drafts and keep autosave keys after deletion."""

import sqlalchemy as sa
from alembic import context, op


revision = "e1d14f94ba37"
down_revision = "0d01383ecab9"
branch_labels = None
depends_on = None

REQUIRED_COLUMNS = {
    "paper_id": sa.Integer(),
    "title": sa.String(255),
    "opens_at": sa.DateTime(),
    "closes_at": sa.DateTime(),
    "duration_minutes": sa.Integer(),
}
COMPLETE_EXAM = " AND ".join(f"{column} IS NOT NULL" for column in REQUIRED_COLUMNS)


def upgrade() -> None:
    op.add_column("exams", sa.Column("autosave_key", sa.String(36), nullable=True))
    op.add_column("exams", sa.Column("discarded_at", sa.DateTime(), nullable=True))
    op.create_unique_constraint("uq_exams_owner_autosave_key", "exams", ["created_by", "autosave_key"])
    op.create_check_constraint("ck_exams_complete_outside_draft", "exams", f"status = 'draft' OR ({COMPLETE_EXAM})")
    for column, kind in REQUIRED_COLUMNS.items():
        op.alter_column("exams", column, existing_type=kind, nullable=True)


def downgrade() -> None:
    if not context.is_offline_mode():
        incomplete = op.get_bind().scalar(sa.text(f"SELECT 1 FROM exams WHERE NOT ({COMPLETE_EXAM}) LIMIT 1"))
        if incomplete is not None:
            raise RuntimeError("Không thể hạ migration khi còn bản nháp chưa đầy đủ hoặc đã xóa.")
    for column, kind in REQUIRED_COLUMNS.items():
        op.alter_column("exams", column, existing_type=kind, nullable=False)
    op.drop_constraint("ck_exams_complete_outside_draft", "exams", type_="check")
    op.drop_constraint("uq_exams_owner_autosave_key", "exams", type_="unique")
    op.drop_column("exams", "discarded_at")
    op.drop_column("exams", "autosave_key")
