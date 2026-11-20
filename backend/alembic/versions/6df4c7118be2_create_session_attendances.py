"""Record student presence at individual class sessions."""

from alembic import op
import sqlalchemy as sa


revision = "6df4c7118be2"
down_revision = "1e5f7b93c204"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "session_attendances",
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["class_sessions.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.user_id"]),
        sa.PrimaryKeyConstraint("session_id", "student_id"),
    )
    op.create_index("ix_session_attendances_student_id", "session_attendances", ["student_id"])


def downgrade() -> None:
    op.drop_table("session_attendances")
