"""fase_33_workflow_intelligence_and_engine

Revision ID: 3d4e5f6a7b8c
Revises: 2c3d4e5f6a7b
Create Date: 2026-08-30 01:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '3d4e5f6a7b8c'
down_revision: Union[str, Sequence[str], None] = '2c3d4e5f6a7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. workflows
    op.create_table(
        'workflows',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('workflow_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_by', sa.String(length=100), nullable=False, server_default='USER'),
        sa.Column('safety_level', sa.String(length=50), nullable=False, server_default='AUTO_LOW_RISK'),
        sa.Column('execution_policy', sa.String(length=50), nullable=False, server_default='SINGLE_ACTIVE'),
        sa.Column('max_runtime_seconds', sa.Integer(), nullable=False, server_default='300'),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='NORMAL'),
        sa.Column('trigger_config', sa.JSON(), nullable=False),
        sa.Column('condition_config', sa.JSON(), nullable=True),
        sa.Column('action_config', sa.JSON(), nullable=True),
        sa.Column('retry_policy', sa.JSON(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workflow_id')
    )
    op.create_index('ix_workflows_workflow_id', 'workflows', ['workflow_id'], unique=True)
    op.create_index('ix_workflows_name', 'workflows', ['name'], unique=False)
    op.create_index('ix_workflows_enabled', 'workflows', ['enabled'], unique=False)
    op.create_index('ix_workflows_status', 'workflows', ['status'], unique=False)

    # 2. workflow_steps
    op.create_table(
        'workflow_steps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('step_id', sa.String(length=100), nullable=False),
        sa.Column('workflow_id', sa.String(length=100), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('condition', sa.JSON(), nullable=True),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('retry_policy', sa.JSON(), nullable=False),
        sa.Column('permission_level', sa.String(length=50), nullable=False, server_default='LOW'),
        sa.Column('requires_confirmation', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('compensating_action', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.workflow_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('step_id')
    )
    op.create_index('ix_workflow_steps_step_id', 'workflow_steps', ['step_id'], unique=True)
    op.create_index('ix_workflow_steps_workflow_id', 'workflow_steps', ['workflow_id'], unique=False)
    op.create_index('ix_workflow_steps_action_type', 'workflow_steps', ['action_type'], unique=False)

    # 3. workflow_executions
    op.create_table(
        'workflow_executions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('execution_id', sa.String(length=100), nullable=False),
        sa.Column('workflow_id', sa.String(length=100), nullable=False),
        sa.Column('workflow_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='RUNNING'),
        sa.Column('current_step_order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('trigger_source', sa.String(length=100), nullable=False, server_default='MANUAL'),
        sa.Column('device_id', sa.String(length=100), nullable=False, server_default='DESKTOP-MAIN'),
        sa.Column('correlation_id', sa.String(length=100), nullable=True),
        sa.Column('is_dry_run', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('result_summary', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.workflow_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('execution_id')
    )
    op.create_index('ix_workflow_executions_execution_id', 'workflow_executions', ['execution_id'], unique=True)
    op.create_index('ix_workflow_executions_workflow_id', 'workflow_executions', ['workflow_id'], unique=False)
    op.create_index('ix_workflow_executions_status', 'workflow_executions', ['status'], unique=False)

    # 4. workflow_step_executions
    op.create_table(
        'workflow_step_executions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('step_execution_id', sa.String(length=100), nullable=False),
        sa.Column('execution_id', sa.String(length=100), nullable=False),
        sa.Column('step_id', sa.String(length=100), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['execution_id'], ['workflow_executions.execution_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('step_execution_id')
    )
    op.create_index('ix_workflow_step_executions_step_execution_id', 'workflow_step_executions', ['step_execution_id'], unique=True)
    op.create_index('ix_workflow_step_executions_execution_id', 'workflow_step_executions', ['execution_id'], unique=False)

    # 5. workflow_confirmations
    op.create_table(
        'workflow_confirmations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('confirmation_id', sa.String(length=100), nullable=False),
        sa.Column('execution_id', sa.String(length=100), nullable=False),
        sa.Column('step_id', sa.String(length=100), nullable=False),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('parameters_summary', sa.JSON(), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False, server_default='MEDIUM'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False, server_default='DESKTOP-MAIN'),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by_device', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['execution_id'], ['workflow_executions.execution_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('confirmation_id')
    )
    op.create_index('ix_workflow_confirmations_confirmation_id', 'workflow_confirmations', ['confirmation_id'], unique=True)
    op.create_index('ix_workflow_confirmations_execution_id', 'workflow_confirmations', ['execution_id'], unique=False)
    op.create_index('ix_workflow_confirmations_status', 'workflow_confirmations', ['status'], unique=False)

    # 6. workflow_recommendations
    op.create_table(
        'workflow_recommendations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('recommendation_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('suggested_workflow', sa.JSON(), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False, server_default='85'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recommendation_id')
    )
    op.create_index('ix_workflow_recommendations_recommendation_id', 'workflow_recommendations', ['recommendation_id'], unique=True)
    op.create_index('ix_workflow_recommendations_status', 'workflow_recommendations', ['status'], unique=False)

def downgrade() -> None:
    pass
