"""Reference student profiles from class enrollments."""

from alembic import op
from sqlalchemy import inspect


revision = "c8b92e36b910"
down_revision = "a37b92d89745"
branch_labels = None
depends_on = None

TABLE = "class_enrollments"
USER_FK = "class_enrollments_ibfk_2"
STUDENT_FK = "fk_class_enrollments_student"


def _replace_student_fk(old_name: str, new_name: str, target: str, target_column: str) -> None:
    if op.get_context().as_sql:
        existing = {old_name}
    else:
        existing = {key["name"] for key in inspect(op.get_bind()).get_foreign_keys(TABLE)}

    # Validate existing rows against the new constraint before dropping the old one.
    if new_name not in existing:
        op.create_foreign_key(new_name, TABLE, target, ["student_id"], [target_column])
    if old_name in existing:
        op.drop_constraint(old_name, TABLE, type_="foreignkey")


def upgrade() -> None:
    _replace_student_fk(USER_FK, STUDENT_FK, "students", "user_id")


def downgrade() -> None:
    _replace_student_fk(STUDENT_FK, USER_FK, "users", "id")
