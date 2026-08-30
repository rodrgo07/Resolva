"""fase_29_remote_and_realtime

Revision ID: 9e0f1a2b3c4d
Revises: 8d9e0f2a3b4c
Create Date: 2026-08-30 00:41:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '9e0f1a2b3c4d'
down_revision: Union[str, Sequence[str], None] = '8d9e0f2a3b4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Tabela remote_commands
    op.create_table(
        'remote_commands',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('request_id', sa.String(length=100), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('command_type', sa.String(length=100), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('permission_level', sa.String(length=50), nullable=False, server_default='READ'),
        sa.Column('risk_level', sa.String(length=50), nullable=False, server_default='LOW'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='EXECUTED'),
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_id')
    )
    op.create_index('ix_remote_commands_request_id', 'remote_commands', ['request_id'], unique=True)
    op.create_index('ix_remote_commands_device_id', 'remote_commands', ['device_id'], unique=False)
    op.create_index('ix_remote_commands_command_type', 'remote_commands', ['command_type'], unique=False)
    op.create_index('ix_remote_commands_status', 'remote_commands', ['status'], unique=False)

    # 2. Tabela remote_pending_actions
    op.create_table(
        'remote_pending_actions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('action_id', sa.String(length=100), nullable=False),
        sa.Column('request_id', sa.String(length=100), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('command_type', sa.String(length=100), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('risk_level', sa.String(length=50), nullable=False, server_default='MEDIUM'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('action_id')
    )
    op.create_index('ix_remote_pending_actions_action_id', 'remote_pending_actions', ['action_id'], unique=True)
    op.create_index('ix_remote_pending_actions_request_id', 'remote_pending_actions', ['request_id'], unique=False)
    op.create_index('ix_remote_pending_actions_device_id', 'remote_pending_actions', ['device_id'], unique=False)
    op.create_index('ix_remote_pending_actions_status', 'remote_pending_actions', ['status'], unique=False)

    # 3. Tabela push_device_tokens
    op.create_table(
        'push_device_tokens',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False, server_default='ANDROID'),
        sa.Column('push_token', sa.String(length=500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('last_registered_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('push_token')
    )
    op.create_index('ix_push_device_tokens_device_id', 'push_device_tokens', ['device_id'], unique=False)
    op.create_index('ix_push_device_tokens_push_token', 'push_device_tokens', ['push_token'], unique=True)
    op.create_index('ix_push_device_tokens_is_active', 'push_device_tokens', ['is_active'], unique=False)

def downgrade() -> None:
    pass
