"""Add providers_schemas foreign key to plan for data blob

Revision ID: eb90e6532fa6
Revises: 5620abf2c8d1
Create Date: 2023-05-01 14:30:46.674556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb90e6532fa6'
down_revision = '5620abf2c8d1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plan', sa.Column('providers_schemas_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'plan', 'blob', ['providers_schemas_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'plan', type_='foreignkey')
    op.drop_column('plan', 'providers_schemas_id')
    # ### end Alembic commands ###
