"""create students table

Revision ID: 00f9ac895c7d
Revises: 87c6e2eb12db
Create Date: 2026-11-19 16:04:06.906753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00f9ac895c7d'
down_revision: Union[str, Sequence[str], None] = '87c6e2eb12db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "students",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.CheckConstraint("grade IN (10, 11, 12)", name="ck_students_grade"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("students")
