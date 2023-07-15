"""Add description field to lifecycle

Revision ID: c27a23b17a83
Revises: 0dd2b62254d3
Create Date: 2023-05-13 16:25:34.686423

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c27a23b17a83'
down_revision = '0dd2b62254d3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lifecycle', sa.Column('description', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('lifecycle', 'description')
    # ### end Alembic commands ###