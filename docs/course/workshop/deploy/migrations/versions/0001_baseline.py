"""Explicit baseline for a NEW learning database, never stamp an existing app."""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users', sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('name', sa.String(100), nullable=False),
                    sa.Column('role', sa.String(30), nullable=False),
                    sa.Column('active', sa.Integer(), nullable=False))
    op.create_table('classes', sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('title', sa.String(200), nullable=False),
                    sa.Column('teacher_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False))
    op.create_index('ix_classes_teacher_id', 'classes', ['teacher_id'])
    op.create_table('memberships', sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('class_id', sa.Integer(), sa.ForeignKey('classes.id'), nullable=False),
                    sa.Column('student_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
                    sa.UniqueConstraint('class_id', 'student_id', name='uq_membership'))
    op.create_table('assignments', sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('class_id', sa.Integer(), sa.ForeignKey('classes.id'), nullable=False),
                    sa.Column('title', sa.String(200), nullable=False), sa.Column('due_at', sa.DateTime()))
    op.create_index('ix_assignments_class_id', 'assignments', ['class_id'])
    op.create_table('submissions', sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('assignment_id', sa.Integer(), sa.ForeignKey('assignments.id'), nullable=False),
                    sa.Column('student_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
                    sa.Column('answer', sa.String(2000), nullable=False),
                    sa.Column('submitted_at', sa.DateTime(), nullable=False),
                    sa.Column('score', sa.Integer()), sa.Column('grade_published', sa.Boolean(), nullable=False),
                    sa.UniqueConstraint('assignment_id', 'student_id', name='uq_submission'),
                    sa.CheckConstraint('score IS NULL OR (score >= 0 AND score <= 10)', name='ck_submission_score'))
    op.create_index('ix_submissions_assignment_id', 'submissions', ['assignment_id'])


def downgrade():
    # Destructive by definition: practice only on a disposable lab copy.
    for table in ['submissions', 'assignments', 'memberships', 'classes', 'users']:
        op.drop_table(table)
