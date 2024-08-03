"""Add status column to state version

Revision ID: 376a843af267
Revises: 6209dfe486dc
Create Date: 2024-08-01 05:31:11.690395

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '376a843af267'
down_revision = '6209dfe486dc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('state_version', sa.Column('status', sa.Enum('PENDING', 'FINALIZED', 'DISCARDED', 'BACKING_DATA_SOFT_DELETED', 'BACKING_DATA_PERMANENTLY_DELETED', name='stateversionstatus'), nullable=False))
    bind = op.get_bind()
    bind.execute("""UPDATE state_version SET status='FINALIZED'""")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('state_version', 'status')
    # ### end Alembic commands ###