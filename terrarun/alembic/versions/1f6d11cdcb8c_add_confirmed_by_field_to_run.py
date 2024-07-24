"""Add confirmed by field to run

Revision ID: 1f6d11cdcb8c
Revises: 7d65f74baa78
Create Date: 2024-07-24 05:53:16.994515

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f6d11cdcb8c'
down_revision = '7d65f74baa78'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('run', sa.Column('confirmed_by_id', sa.Integer(), nullable=True))
    op.create_foreign_key('run_confirmed_by_id_user_id', 'run', 'user', ['confirmed_by_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('run_confirmed_by_id_user_id', 'run', type_='foreignkey')
    op.drop_column('run', 'confirmed_by_id')
    # ### end Alembic commands ###
