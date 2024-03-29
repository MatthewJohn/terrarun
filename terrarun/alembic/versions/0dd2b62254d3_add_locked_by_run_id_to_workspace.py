"""Add locked by run ID to workspace

Revision ID: 0dd2b62254d3
Revises: b542a7866a21
Create Date: 2023-05-13 13:52:45.853913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0dd2b62254d3'
down_revision = 'b542a7866a21'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workspace', sa.Column('locked_by_run_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_workspace_locked_by_run_id_run_id', 'workspace', 'run', ['locked_by_run_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_workspace_locked_by_run_id_run_id', 'workspace', type_='foreignkey')
    op.drop_column('workspace', 'locked_by_run_id')
    # ### end Alembic commands ###
