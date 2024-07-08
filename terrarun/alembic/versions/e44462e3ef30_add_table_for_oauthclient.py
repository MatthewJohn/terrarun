"""Add table for OauthClient

Revision ID: e44462e3ef30
Revises: e83d81428173
Create Date: 2023-05-02 15:53:10.517028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e44462e3ef30'
down_revision = 'e83d81428173'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('oauth_client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('key', sa.String(length=128), nullable=False),
    sa.Column('http_url', sa.String(length=128), nullable=False),
    sa.Column('api_url', sa.String(length=128), nullable=False),
    sa.Column('oauth_token_string', sa.String(length=128), nullable=False),
    sa.Column('private_key', sa.String(length=128), nullable=True),
    sa.Column('secret', sa.String(length=128), nullable=False),
    sa.Column('rsa_public_key', sa.String(length=128), nullable=True),
    sa.Column('service_provider', sa.Enum('GITHUB', 'GITHUB_ENTERPRISE', 'GITLAB_HOSTED', 'GITLAB_COMMUNITY_EDITION', 'GITLAB_ENTERPRISE_EDITION', 'ADO_SERVER', name='oauthserviceprovider'), nullable=False),
    sa.Column('callback_id', sa.String(length=128), nullable=False),
    sa.Column('organisation_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['organisation_id'], ['organisation.id'], name='fk_openid_client_organisation_id_organisation_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('callback_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('oauth_client')
    # ### end Alembic commands ###