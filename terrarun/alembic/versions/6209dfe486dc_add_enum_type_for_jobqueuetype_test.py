"""Add enum type for JobQueueType TEST

Revision ID: 6209dfe486dc
Revises: 8608a9d79329
Create Date: 2024-08-01 05:04:44.703004

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6209dfe486dc'
down_revision = '8608a9d79329'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('run_queue', 'job_type',
        existing_type=sa.Enum(
            'PLAN', 'APPLY', 'POLICY', 'ASSESSMENT', name='jobqueuetype'),
        type_=sa.Enum(
            'PLAN', 'APPLY', 'POLICY', 'ASSESSMENT', 'TEST', name='jobqueuetype'),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('run_queue', 'job_type',
        existing_type=sa.Enum(
            'PLAN', 'APPLY', 'POLICY', 'ASSESSMENT', 'TEST', name='jobqueuetype'),
        type_=sa.Enum(
            'PLAN', 'APPLY', 'POLICY', 'ASSESSMENT', name='jobqueuetype'),
    )
    # ### end Alembic commands ###
