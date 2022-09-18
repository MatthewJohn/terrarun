"""Add task_stage and task_result models

Revision ID: 0fc7c4dd47a6
Revises: f4ebc77f2486
Create Date: 2022-09-18 07:32:19.825194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fc7c4dd47a6'
down_revision = 'f4ebc77f2486'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task_stage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stage', sa.Enum('PRE_PLAN', 'POST_PLAN', 'POST_APPLY', name='workspacetaskstage'), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'PASSED', 'FAILED', 'ERRRORED', 'CANCELED', 'UNREACHABLE', name='taskstagestatus'), nullable=True),
    sa.Column('run_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['run_id'], ['run.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task_result',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'PASSED', 'FAILED', 'ERRRORED', 'CANCELED', 'UNREACHABLE', name='taskresultstatus'), nullable=True),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.Column('task_stage_id', sa.Integer(), nullable=False),
    sa.Column('workspace_task_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['blob.id'], ),
    sa.ForeignKeyConstraint(['task_stage_id'], ['task_stage.id'], ),
    sa.ForeignKeyConstraint(['workspace_task_id'], ['workspace_task.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_result')
    op.drop_table('task_stage')
    # ### end Alembic commands ###