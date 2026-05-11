"""Add professional development fields to student profiles

Revision ID: prof_dev_001
Revises: 2a2390615e09
Create Date: 2026-05-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'prof_dev_001'
down_revision = '2a2390615e09'
branch_labels = None
depends_on = None


def upgrade():
    # Add three new columns to student_profiles table
    op.add_column('student_profiles', sa.Column('internship_details', sa.Text(), nullable=True))
    op.add_column('student_profiles', sa.Column('nptel', sa.Text(), nullable=True))
    op.add_column('student_profiles', sa.Column('final_year_project', sa.Text(), nullable=True))


def downgrade():
    # Remove the new columns if migration is reverted
    op.drop_column('student_profiles', 'final_year_project')
    op.drop_column('student_profiles', 'nptel')
    op.drop_column('student_profiles', 'internship_details')
