"""Add indexes to API ID table

Revision ID: 39e8a680df30
Revises: 614792b159a0
Create Date: 2023-05-08 08:05:56.092727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39e8a680df30'
down_revision = '614792b159a0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('_api_id_suffix_index', 'api_id', ['api_id_suffix'], unique=False)
    op.create_index('_object_class_object_id_in', 'api_id', ['object_class', 'object_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('_object_class_object_id_in', table_name='api_id')
    op.drop_index('_api_id_suffix_index', table_name='api_id')
    # ### end Alembic commands ###