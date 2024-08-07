"""Add default agent pool to environment and project

Revision ID: b3ce0af0c015
Revises: 1f6d11cdcb8c
Create Date: 2024-07-28 05:25:43.084912

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b3ce0af0c015'
down_revision = '1f6d11cdcb8c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('environment', sa.Column('default_agent_pool_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_environment_default_agent_pool_id', 'environment', 'agent_pool', ['default_agent_pool_id'], ['id'])
    op.add_column('project', sa.Column('default_agent_pool_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_project_default_agent_pool_id', 'project', 'agent_pool', ['default_agent_pool_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_project_default_agent_pool_id', 'project', type_='foreignkey')
    op.drop_column('project', 'default_agent_pool_id')
    op.drop_constraint('fk_environment_default_agent_pool_id', 'environment', type_='foreignkey')
    op.drop_column('environment', 'default_agent_pool_id')
    # ### end Alembic commands ###
