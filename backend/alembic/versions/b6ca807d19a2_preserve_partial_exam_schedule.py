"""preserve partial exam schedule inputs"""

import sqlalchemy as sa
from alembic import op

revision = "b6ca807d19a2"
down_revision = "e1d14f94ba37"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("exams", sa.Column("schedule_inputs", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("exams", "schedule_inputs")
