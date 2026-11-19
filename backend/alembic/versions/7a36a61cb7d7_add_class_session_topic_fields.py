"""add class session topic fields

Revision ID: 7a36a61cb7d7
Revises: 00f9ac895c7d
Create Date: 2026-11-19 16:19:02.741745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a36a61cb7d7'
down_revision: Union[str, Sequence[str], None] = '00f9ac895c7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Existing sessions need a topic before the database can require one.
    op.add_column(
        "class_sessions",
        sa.Column(
            "topic",
            sa.String(length=255),
            nullable=False,
            server_default="Chưa cập nhật chủ đề",
        ),
    )
    op.add_column("class_sessions", sa.Column("has_algebra", sa.Boolean(), nullable=True))
    op.add_column("class_sessions", sa.Column("has_geometry", sa.Boolean(), nullable=True))
    op.add_column("class_sessions", sa.Column("is_review", sa.Boolean(), nullable=True))
    op.alter_column(
        "class_sessions",
        "topic",
        existing_type=sa.String(length=255),
        existing_nullable=False,
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("class_sessions", "is_review")
    op.drop_column("class_sessions", "has_geometry")
    op.drop_column("class_sessions", "has_algebra")
    op.drop_column("class_sessions", "topic")
