"""Add user table

Revision ID: 7a614fb13221
Revises: 9917c4e05b97
Create Date: 2022-07-31 10:49:38.487862

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a614fb13221'
down_revision = '9917c4e05b97'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('salt', sa.BLOB(), nullable=True),
    sa.Column('password', sa.BLOB(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('service_account', sa.Boolean(), nullable=True),
    sa.Column('site_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('user_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('USER_GENERATED', 'UI', name='usertokentype'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_used', sa.DateTime(), nullable=True),
    sa.Column('expiry', sa.DateTime(), nullable=True),
    sa.Column('token', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_token')
    op.drop_table('user')
    # ### end Alembic commands ###