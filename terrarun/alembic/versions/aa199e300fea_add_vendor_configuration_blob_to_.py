"""Add vendor configuration blob to authorised repo

Revision ID: aa199e300fea
Revises: 69fde16a2c60
Create Date: 2023-05-07 09:51:29.786006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa199e300fea'
down_revision = '69fde16a2c60'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('authorised_repo', sa.Column('vendor_configuration_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'authorised_repo', 'blob', ['vendor_configuration_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'authorised_repo', type_='foreignkey')
    op.drop_column('authorised_repo', 'vendor_configuration_id')
    # ### end Alembic commands ###
