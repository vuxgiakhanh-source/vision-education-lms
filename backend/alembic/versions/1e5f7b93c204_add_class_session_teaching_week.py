"""Store the teaching week of each class session."""

from alembic import op
import sqlalchemy as sa


revision = "1e5f7b93c204"
down_revision = "c8b92e36b910"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("class_sessions", sa.Column("teaching_week", sa.Integer(), nullable=True))
    op.create_check_constraint(
        "ck_class_sessions_teaching_week", "class_sessions", "teaching_week >= 1"
    )


def downgrade() -> None:
    op.drop_constraint("ck_class_sessions_teaching_week", "class_sessions", type_="check")
    op.drop_column("class_sessions", "teaching_week")
