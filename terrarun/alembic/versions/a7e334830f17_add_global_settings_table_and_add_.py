"""Add global settings table and add settings for SAML

Revision ID: a7e334830f17
Revises: d3166f10030f
Create Date: 2023-07-21 05:46:51.128454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7e334830f17'
down_revision = 'd3166f10030f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('global_setting',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('data_type', sa.String(length=128), nullable=False),
    sa.Column('value', sa.String(length=1024), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    # Example to add settings to global settings table
    # bind = op.get_bind()
    # for name, data_type, value in [
    #         ]:
    #     bind.execute(
    #         sa.sql.text("""INSERT INTO global_setting(name, data_type, value) VALUES(:name, :data_type, :value)"""),
    #         name=name,
    #         data_type=data_type,
    #         value=value
    #     )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('global_setting')
    # ### end Alembic commands ###