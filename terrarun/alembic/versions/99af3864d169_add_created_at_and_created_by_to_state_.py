"""Add created_at and created_by to state version

Revision ID: 99af3864d169
Revises: 73ceef3841a1
Create Date: 2024-07-14 06:46:07.233679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99af3864d169'
down_revision = '73ceef3841a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('state_version', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('state_version', sa.Column('created_by_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'state_version', 'user', ['created_by_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'state_version', type_='foreignkey')
    op.drop_column('state_version', 'created_by_id')
    op.drop_column('state_version', 'created_at')
    # ### end Alembic commands ###
