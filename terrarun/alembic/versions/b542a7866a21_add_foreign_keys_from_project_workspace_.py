"""Add foreign keys from project/workspace/run to tool for terraform version

Revision ID: b542a7866a21
Revises: 7f5d46e26c9d
Create Date: 2023-05-13 07:56:42.013784

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b542a7866a21'
down_revision = '7f5d46e26c9d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('tool_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'project', 'tool', ['tool_id'], ['id'])
    op.drop_column('project', 'terraform_version')
    op.add_column('run', sa.Column('tool_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'run', 'tool', ['tool_id'], ['id'])
    op.drop_column('run', 'terraform_version')
    op.add_column('workspace', sa.Column('tool_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'workspace', 'tool', ['tool_id'], ['id'])
    op.drop_column('workspace', 'terraform_version')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workspace', sa.Column('terraform_version', mysql.VARCHAR(length=128), nullable=True))
    op.drop_constraint(None, 'workspace', type_='foreignkey')
    op.drop_column('workspace', 'tool_id')
    op.add_column('run', sa.Column('terraform_version', mysql.VARCHAR(length=128), nullable=True))
    op.drop_constraint(None, 'run', type_='foreignkey')
    op.drop_column('run', 'tool_id')
    op.add_column('project', sa.Column('terraform_version', mysql.VARCHAR(length=128), nullable=True))
    op.drop_constraint(None, 'project', type_='foreignkey')
    op.drop_column('project', 'tool_id')
    # ### end Alembic commands ###
