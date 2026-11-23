"""Add pending reconfirmation to temporary transfers."""

import sqlalchemy as sa
from alembic import op


revision = "1a9b7f4e3d21"
down_revision = "0bc3c79e6152"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sessions_transfers",
        sa.Column("requires_confirmation", sa.Boolean(), nullable=False, server_default="0"),
    )


def downgrade():
    op.drop_column("sessions_transfers", "requires_confirmation")
