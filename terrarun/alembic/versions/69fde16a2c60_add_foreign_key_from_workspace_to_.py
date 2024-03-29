"""Add foreign key from workspace to authorised repo, removing old columns

Revision ID: 69fde16a2c60
Revises: fcebb3b28fb6
Create Date: 2023-05-06 05:26:40.255789

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '69fde16a2c60'
down_revision = 'fcebb3b28fb6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workspace', sa.Column('authorised_repo_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_workspace_authorised_repo_id_authorised_repo_id', 'workspace', 'authorised_repo', ['authorised_repo_id'], ['id'])
    op.drop_column('workspace', 'vcs_repo_identifier')
    op.drop_column('workspace', 'vcs_repo')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workspace', sa.Column('vcs_repo', mysql.VARCHAR(length=128), nullable=True))
    op.add_column('workspace', sa.Column('vcs_repo_identifier', mysql.VARCHAR(length=128), nullable=True))
    op.drop_constraint('fk_workspace_authorised_repo_id_authorised_repo_id', 'workspace', type_='foreignkey')
    op.drop_column('workspace', 'authorised_repo_id')
    # ### end Alembic commands ###
