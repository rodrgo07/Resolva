"""fase_35_hardening_and_observability

Revision ID: 5f6a7b8c9d0e
Revises: 4e5f6a7b8c9d
Create Date: 2026-08-30 03:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '5f6a7b8c9d0e'
down_revision: Union[str, Sequence[str], None] = '4e5f6a7b8c9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # 1. system_health_records
    if 'system_health_records' not in existing_tables:
        op.create_table(
            'system_health_records',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('check_id', sa.String(length=100), nullable=False),
            sa.Column('overall_status', sa.String(length=50), nullable=False, server_default='HEALTHY'),
            sa.Column('safe_mode_active', sa.Boolean(), nullable=False, server_default=sa.text('0')),
            sa.Column('components_status', sa.JSON(), nullable=False),
            sa.Column('diagnostics', sa.JSON(), nullable=False),
            sa.Column('metrics_summary', sa.JSON(), nullable=True),
            sa.Column('checked_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('check_id')
        )
        op.create_index('ix_system_health_records_check_id', 'system_health_records', ['check_id'], unique=True)

    # 2. safety_policy_settings
    if 'safety_policy_settings' not in existing_tables:
        op.create_table(
            'safety_policy_settings',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('key', sa.String(length=100), nullable=False),
            sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
            sa.Column('autonomy_level', sa.String(length=50), nullable=False, server_default='LEVEL_3_LOW_RISK_AUTO'),
            sa.Column('description', sa.String(length=255), nullable=True),
            sa.Column('config', sa.JSON(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('key')
        )
        op.create_index('ix_safety_policy_settings_key', 'safety_policy_settings', ['key'], unique=True)

    # 3. audit_event_logs
    if 'audit_event_logs' not in existing_tables:
        op.create_table(
            'audit_event_logs',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('audit_id', sa.String(length=100), nullable=False),
            sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('source', sa.String(length=100), nullable=False, server_default='SYSTEM'),
            sa.Column('device_id', sa.String(length=100), nullable=False, server_default='DESKTOP-MAIN'),
            sa.Column('actor', sa.String(length=100), nullable=False, server_default='USER'),
            sa.Column('action', sa.String(length=100), nullable=False),
            sa.Column('risk', sa.String(length=50), nullable=False, server_default='LOW'),
            sa.Column('status', sa.String(length=50), nullable=False, server_default='SUCCESS'),
            sa.Column('reason', sa.String(length=255), nullable=True),
            sa.Column('details', sa.JSON(), nullable=True),
            sa.Column('correlation_id', sa.String(length=100), nullable=True),
            sa.Column('trace_id', sa.String(length=100), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('audit_id')
        )
        op.create_index('ix_audit_event_logs_audit_id', 'audit_event_logs', ['audit_id'], unique=True)
        op.create_index('ix_audit_event_logs_timestamp', 'audit_event_logs', ['timestamp'], unique=False)
        op.create_index('ix_audit_event_logs_correlation_id', 'audit_event_logs', ['correlation_id'], unique=False)

def downgrade() -> None:
    pass
