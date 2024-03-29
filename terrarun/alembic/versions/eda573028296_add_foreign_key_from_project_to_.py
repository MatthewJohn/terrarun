"""Add foreign key from project to authorised repo, removing old columns

Revision ID: eda573028296
Revises: 94c621ca2c39
Create Date: 2023-05-06 05:11:37.396646

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'eda573028296'
down_revision = '94c621ca2c39'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('authorised_repo_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_project_authorised_repo_id_authorised_repo_id', 'project', 'authorised_repo', ['authorised_repo_id'], ['id'])
    op.drop_column('project', 'vcs_repo')
    op.drop_column('project', 'vcs_repo_identifier')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('vcs_repo_identifier', mysql.VARCHAR(length=128), nullable=True))
    op.add_column('project', sa.Column('vcs_repo', mysql.VARCHAR(length=128), nullable=True))
    op.drop_constraint('fk_project_authorised_repo_id_authorised_repo_id', 'project', type_='foreignkey')
    op.drop_column('project', 'authorised_repo_id')
    # ### end Alembic commands ###
