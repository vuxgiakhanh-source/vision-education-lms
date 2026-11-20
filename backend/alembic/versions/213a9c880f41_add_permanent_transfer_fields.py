"""Store the lesson boundary for a permanent transfer."""

from alembic import op
import sqlalchemy as sa


revision = "213a9c880f41"
down_revision = "6df4c7118be2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("class_enrollments") as table:
        table.add_column(sa.Column("completed_through_teaching_week", sa.Integer()))
        table.add_column(sa.Column("entry_session_id", sa.Integer()))
        table.create_foreign_key(
            "fk_class_enrollments_entry_session", "class_sessions", ["entry_session_id"], ["id"]
        )
    op.add_column("sessions_transfers", sa.Column("superseded_at", sa.DateTime()))


def downgrade() -> None:
    op.drop_column("sessions_transfers", "superseded_at")
    with op.batch_alter_table("class_enrollments") as table:
        table.drop_constraint("fk_class_enrollments_entry_session", type_="foreignkey")
        table.drop_column("entry_session_id")
        table.drop_column("completed_through_teaching_week")
