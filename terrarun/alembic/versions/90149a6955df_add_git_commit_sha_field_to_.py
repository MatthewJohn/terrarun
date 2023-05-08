"""Add git commit sha field to configuration version

Revision ID: 90149a6955df
Revises: 9afeb4e61715
Create Date: 2023-05-08 15:31:37.174335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90149a6955df'
down_revision = '9afeb4e61715'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('configuration_version', sa.Column('git_commit_sha', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('configuration_version', 'git_commit_sha')
    # ### end Alembic commands ###
