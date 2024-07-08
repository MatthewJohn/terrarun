"""Add table for tools

Revision ID: 55527de9c93d
Revises: 3ce56b652bfc
Create Date: 2023-05-12 05:41:21.713305

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55527de9c93d'
down_revision = '3ce56b652bfc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tool',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('api_id_fk', sa.Integer(), nullable=True),
    sa.Column('tool_type', sa.Enum('TERRAFORM_VERSION', name='tooltype'), nullable=False),
    sa.Column('version', sa.String(length=128), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=True),
    sa.Column('deprecated', sa.Boolean(), nullable=True),
    sa.Column('deprecated_reason', sa.String(length=128), nullable=True),
    sa.Column('url', sa.String(length=128), nullable=True),
    sa.Column('checksum_url', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['api_id_fk'], ['api_id.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tool')
    # ### end Alembic commands ###