"""create sessions transfers table

Revision ID: a37b92d89745
Revises: 7a36a61cb7d7
Create Date: 2026-11-19 16:22:18.992453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a37b92d89745'
down_revision: Union[str, Sequence[str], None] = '7a36a61cb7d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sessions_transfers",
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("original_session_id", sa.Integer(), nullable=False),
        sa.Column("replacement_sessions_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("student_id", "original_session_id"),
        sa.ForeignKeyConstraint(["student_id"], ["students.user_id"]),
        sa.ForeignKeyConstraint(["original_session_id"], ["class_sessions.id"]),
        sa.ForeignKeyConstraint(["replacement_sessions_id"], ["class_sessions.id"]),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("sessions_transfers")
