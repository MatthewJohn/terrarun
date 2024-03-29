"""Make oauth_token service_provider_user nullable

Revision ID: 4064184c1353
Revises: afd5cc42b6db
Create Date: 2023-05-03 16:28:34.910774

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4064184c1353'
down_revision = 'afd5cc42b6db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('oauth_token', 'service_provider_user',
               existing_type=mysql.VARCHAR(length=128),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('oauth_token', 'service_provider_user',
               existing_type=mysql.VARCHAR(length=128),
               nullable=False)
    # ### end Alembic commands ###
