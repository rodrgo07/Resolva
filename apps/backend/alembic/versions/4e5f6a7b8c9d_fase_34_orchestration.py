"""fase_34_orchestration_and_adaptive_workflows

Revision ID: 4e5f6a7b8c9d
Revises: 3d4e5f6a7b8c
Create Date: 2026-08-30 01:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '4e5f6a7b8c9d'
down_revision: Union[str, Sequence[str], None] = '3d4e5f6a7b8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. orchestration_runs
    op.create_table(
        'orchestration_runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('run_id', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='RUNNING'),
        sa.Column('trigger_type', sa.String(length=50), nullable=False, server_default='MANUAL'),
        sa.Column('trigger_source', sa.String(length=100), nullable=False, server_default='USER'),
        sa.Column('device_id', sa.String(length=100), nullable=False, server_default='DESKTOP-MAIN'),
        sa.Column('correlation_id', sa.String(length=100), nullable=True),
        sa.Column('idempotency_key', sa.String(length=100), nullable=True),
        sa.Column('is_dry_run', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('total_steps', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_steps', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('plan_snapshot', sa.JSON(), nullable=False),
        sa.Column('context_snapshot', sa.JSON(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('run_id'),
        sa.UniqueConstraint('idempotency_key')
    )
    op.create_index('ix_orchestration_runs_run_id', 'orchestration_runs', ['run_id'], unique=True)
    op.create_index('ix_orchestration_runs_status', 'orchestration_runs', ['status'], unique=False)
    op.create_index('ix_orchestration_runs_correlation_id', 'orchestration_runs', ['correlation_id'], unique=False)

    # 2. workflow_event_rules
    op.create_table(
        'workflow_event_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('rule_id', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('workflow_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('conditions', sa.JSON(), nullable=True),
        sa.Column('cooldown_seconds', sa.Integer(), nullable=False, server_default='300'),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='NORMAL'),
        sa.Column('requires_confirmation', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rule_id')
    )
    op.create_index('ix_workflow_event_rules_rule_id', 'workflow_event_rules', ['rule_id'], unique=True)
    op.create_index('ix_workflow_event_rules_event_type', 'workflow_event_rules', ['event_type'], unique=False)
    op.create_index('ix_workflow_event_rules_enabled', 'workflow_event_rules', ['enabled'], unique=False)

    # 3. workflow_dependencies
    op.create_table(
        'workflow_dependencies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('dependency_id', sa.String(length=100), nullable=False),
        sa.Column('parent_workflow_id', sa.String(length=100), nullable=False),
        sa.Column('child_workflow_id', sa.String(length=100), nullable=False),
        sa.Column('on_failure_policy', sa.String(length=50), nullable=False, server_default='FAIL_FAST'),
        sa.Column('condition', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dependency_id')
    )
    op.create_index('ix_workflow_dependencies_dependency_id', 'workflow_dependencies', ['dependency_id'], unique=True)

    # 4. workflow_feedbacks
    op.create_table(
        'workflow_feedbacks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('feedback_id', sa.String(length=100), nullable=False),
        sa.Column('orchestration_run_id', sa.String(length=100), nullable=True),
        sa.Column('workflow_id', sa.String(length=100), nullable=False),
        sa.Column('action_type', sa.String(length=100), nullable=True),
        sa.Column('user_action', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('device_id', sa.String(length=100), nullable=False, server_default='DESKTOP-MAIN'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['orchestration_run_id'], ['orchestration_runs.run_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('feedback_id')
    )
    op.create_index('ix_workflow_feedbacks_feedback_id', 'workflow_feedbacks', ['feedback_id'], unique=True)
    op.create_index('ix_workflow_feedbacks_workflow_id', 'workflow_feedbacks', ['workflow_id'], unique=False)

    # 5. workflow_explanations
    op.create_table(
        'workflow_explanations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('explanation_id', sa.String(length=100), nullable=False),
        sa.Column('orchestration_run_id', sa.String(length=100), nullable=True),
        sa.Column('workflow_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('factors', sa.JSON(), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False, server_default='85'),
        sa.Column('source_data', sa.JSON(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['orchestration_run_id'], ['orchestration_runs.run_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('explanation_id')
    )
    op.create_index('ix_workflow_explanations_explanation_id', 'workflow_explanations', ['explanation_id'], unique=True)
    op.create_index('ix_workflow_explanations_workflow_id', 'workflow_explanations', ['workflow_id'], unique=False)

def downgrade() -> None:
    pass
