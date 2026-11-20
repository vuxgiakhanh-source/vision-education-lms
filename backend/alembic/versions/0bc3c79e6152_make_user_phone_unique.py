"""Enforce one account per login phone number."""

import sqlalchemy as sa
from alembic import op


revision = "0bc3c79e6152"
down_revision = "213a9c880f41"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not op.get_context().as_sql:
        duplicate = op.get_bind().execute(
            sa.text("SELECT 1 FROM users GROUP BY phone_number HAVING COUNT(*) > 1 LIMIT 1")
        ).first()
        if duplicate is not None:
            raise RuntimeError("Resolve duplicate user phone numbers before applying uq_users_phone_number.")
    op.create_unique_constraint("uq_users_phone_number", "users", ["phone_number"])


def downgrade() -> None:
    op.drop_constraint("uq_users_phone_number", "users", type_="unique")
