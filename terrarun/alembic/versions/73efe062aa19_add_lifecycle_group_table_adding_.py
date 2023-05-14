"""Add lifecycle group table, adding between relationships of lifecycle environment and lifecycle

Revision ID: 73efe062aa19
Revises: 13c03b88893e
Create Date: 2023-05-14 07:01:53.434594

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '73efe062aa19'
down_revision = '13c03b88893e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('lifecycle_environment', 'environment_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.create_foreign_key('fk_lifecycle_environment_lifecycle_environment_group_id', 'lifecycle_environment', 'lifecycle_environment_group', ['lifecycle_environment_group_id'], ['id'])
    op.drop_column('lifecycle_environment', 'lifecycle_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lifecycle_environment', sa.Column('lifecycle_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_constraint('fk_lifecycle_environment_lifecycle_environment_group_id', 'lifecycle_environment', type_='foreignkey')
    op.alter_column('lifecycle_environment', 'environment_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    # ### end Alembic commands ###
