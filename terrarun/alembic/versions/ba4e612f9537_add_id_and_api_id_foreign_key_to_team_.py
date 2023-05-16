"""Add ID and API ID foreign key to team user membership

Revision ID: ba4e612f9537
Revises: 4a1d3e284ed7
Create Date: 2023-05-14 17:35:50.113025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba4e612f9537'
down_revision = '4a1d3e284ed7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("""
    ALTER table team_user_membership
        ADD id INT NOT NULL AUTO_INCREMENT,
        DROP FOREIGN KEY team_user_membership_ibfk_1,
        DROP FOREIGN KEY team_user_membership_ibfk_2,
        DROP PRIMARY KEY,
        ADD PRIMARY KEY (id),
        ADD FOREIGN KEY (`team_id`) REFERENCES `team` (`id`),
        ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
    """)
    op.add_column('team_user_membership', sa.Column('api_id_fk', sa.Integer(), nullable=True))
    op.create_unique_constraint('_team_id_user_id_uc', 'team_user_membership', ['team_id', 'user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('team_user_membership_api_id', 'team_user_membership', type_='foreignkey')
    op.drop_constraint('_team_id_user_id_uc', 'team_user_membership', type_='unique')
    op.drop_column('team_user_membership', 'api_id_fk')
    op.drop_column('team_user_membership', 'id')
    # ### end Alembic commands ###
