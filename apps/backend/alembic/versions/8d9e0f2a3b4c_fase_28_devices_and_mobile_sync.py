"""fase_28_devices_and_mobile_sync

Revision ID: 8d9e0f2a3b4c
Revises: 7c8e9f1a2b3c
Create Date: 2026-08-29 23:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '8d9e0f2a3b4c'
down_revision: Union[str, Sequence[str], None] = '7c8e9f1a2b3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Tabela devices
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('device_name', sa.String(length=255), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False, server_default='ANDROID'),
        sa.Column('app_version', sa.String(length=50), nullable=False, server_default='0.1.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('is_trusted', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('last_seen_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('paired_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('client_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_id')
    )
    op.create_index('ix_devices_device_id', 'devices', ['device_id'], unique=True)
    op.create_index('ix_devices_platform', 'devices', ['platform'], unique=False)
    op.create_index('ix_devices_status', 'devices', ['status'], unique=False)
    op.create_index('ix_devices_last_seen_at', 'devices', ['last_seen_at'], unique=False)

    # 2. Tabela device_sessions
    op.create_table(
        'device_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('refresh_token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_ip', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token'),
        sa.UniqueConstraint('refresh_token')
    )
    op.create_index('ix_device_sessions_device_id', 'device_sessions', ['device_id'], unique=False)
    op.create_index('ix_device_sessions_session_token', 'device_sessions', ['session_token'], unique=True)
    op.create_index('ix_device_sessions_expires_at', 'device_sessions', ['expires_at'], unique=False)
    op.create_index('ix_device_sessions_is_revoked', 'device_sessions', ['is_revoked'], unique=False)

    # 3. Tabela pairing_requests
    op.create_table(
        'pairing_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('pairing_code', sa.String(length=20), nullable=False),
        sa.Column('qr_payload', sa.String(length=500), nullable=False),
        sa.Column('nonce', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('desktop_device_id', sa.String(length=100), nullable=False, server_default='RESOLVA-DESKTOP-MAIN'),
        sa.Column('server_endpoint', sa.String(length=255), nullable=False, server_default='http://127.0.0.1:8700'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('pairing_code'),
        sa.UniqueConstraint('qr_payload'),
        sa.UniqueConstraint('nonce')
    )
    op.create_index('ix_pairing_requests_pairing_code', 'pairing_requests', ['pairing_code'], unique=True)
    op.create_index('ix_pairing_requests_status', 'pairing_requests', ['status'], unique=False)
    op.create_index('ix_pairing_requests_expires_at', 'pairing_requests', ['expires_at'], unique=False)

    # 4. Tabela sync_operations
    op.create_table(
        'sync_operations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('operation_id', sa.String(length=100), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('operation', sa.String(length=50), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='APPLIED'),
        sa.Column('applied_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('operation_id')
    )
    op.create_index('ix_sync_operations_operation_id', 'sync_operations', ['operation_id'], unique=True)
    op.create_index('ix_sync_operations_device_id', 'sync_operations', ['device_id'], unique=False)
    op.create_index('ix_sync_operations_entity_type', 'sync_operations', ['entity_type'], unique=False)
    op.create_index('ix_sync_operations_entity_id', 'sync_operations', ['entity_id'], unique=False)
    op.create_index('ix_sync_operations_applied_at', 'sync_operations', ['applied_at'], unique=False)

def downgrade() -> None:
    pass
