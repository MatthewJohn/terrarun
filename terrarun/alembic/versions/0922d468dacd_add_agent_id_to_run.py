"""Add agent ID to run

Revision ID: 0922d468dacd
Revises: c0bad5f1483f
Create Date: 2023-05-01 10:06:30.460360

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0922d468dacd'
down_revision = 'c0bad5f1483f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('run_queue', sa.Column('agent_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'run_queue', 'agent', ['agent_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'run_queue', type_='foreignkey')
    op.drop_column('run_queue', 'agent_id')
    # ### end Alembic commands ###
