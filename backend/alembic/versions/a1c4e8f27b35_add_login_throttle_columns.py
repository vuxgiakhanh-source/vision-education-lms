"""Count failed logins per account to slow down password guessing.

Revision ID: a1c4e8f27b35
Revises: 1a9b7f4e3d21
"""
from alembic import op
import sqlalchemy as sa

revision = "a1c4e8f27b35"
down_revision = "1a9b7f4e3d21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("last_failed_login_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "last_failed_login_at")
    op.drop_column("users", "failed_login_count")
