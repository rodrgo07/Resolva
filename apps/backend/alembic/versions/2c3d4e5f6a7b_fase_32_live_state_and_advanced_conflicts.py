"""fase_32_live_state_and_advanced_conflicts

Revision ID: 2c3d4e5f6a7b
Revises: 1b2c3d4e5f6a
Create Date: 2026-08-30 01:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '2c3d4e5f6a7b'
down_revision: Union[str, Sequence[str], None] = '1b2c3d4e5f6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. live_sessions
    op.create_table(
        'live_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('origin_device_id', sa.String(length=100), nullable=False, server_default='DESKTOP-MAIN'),
        sa.Column('user_id', sa.String(length=100), nullable=False, server_default='user_default'),
        sa.Column('type', sa.String(length=50), nullable=False, server_default='POMODORO'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='IDLE'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('paused_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=False, server_default='1500'),
        sa.Column('remaining_seconds', sa.Integer(), nullable=False, server_default='1500'),
        sa.Column('current_block_id', sa.String(length=100), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index('ix_live_sessions_session_id', 'live_sessions', ['session_id'], unique=True)
    op.create_index('ix_live_sessions_device_id', 'live_sessions', ['device_id'], unique=False)
    op.create_index('ix_live_sessions_type', 'live_sessions', ['type'], unique=False)
    op.create_index('ix_live_sessions_status', 'live_sessions', ['status'], unique=False)
    op.create_index('ix_live_sessions_type_status', 'live_sessions', ['type', 'status'], unique=False)

    # 2. device_presences
    op.create_table(
        'device_presences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('device_name', sa.String(length=255), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False, server_default='ANDROID'),
        sa.Column('app_version', sa.String(length=50), nullable=False, server_default='0.1.0'),
        sa.Column('is_online', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('last_heartbeat_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('sync_status', sa.String(length=50), nullable=False, server_default='SYNCED'),
        sa.Column('client_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_id')
    )
    op.create_index('ix_device_presences_device_id', 'device_presences', ['device_id'], unique=True)
    op.create_index('ix_device_presences_is_online', 'device_presences', ['is_online'], unique=False)
    op.create_index('ix_device_presences_last_heartbeat_at', 'device_presences', ['last_heartbeat_at'], unique=False)

    # 3. realtime_events
    op.create_table(
        'realtime_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sequence', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('event_id', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sequence'),
        sa.UniqueConstraint('event_id')
    )
    op.create_index('ix_realtime_events_sequence', 'realtime_events', ['sequence'], unique=True)
    op.create_index('ix_realtime_events_event_id', 'realtime_events', ['event_id'], unique=True)
    op.create_index('ix_realtime_events_event_type', 'realtime_events', ['event_type'], unique=False)
    op.create_index('ix_realtime_events_device_id', 'realtime_events', ['device_id'], unique=False)

    # 4. entity_versions
    op.create_table(
        'entity_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('updated_by_device', sa.String(length=100), nullable=False, server_default='DESKTOP-MAIN'),
        sa.Column('last_payload', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_entity_versions_type_id', 'entity_versions', ['entity_type', 'entity_id'], unique=True)

    # 5. advanced_sync_conflicts
    op.create_table(
        'advanced_sync_conflicts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('conflict_id', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('base_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('local_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('remote_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('local_payload', sa.JSON(), nullable=False),
        sa.Column('remote_payload', sa.JSON(), nullable=False),
        sa.Column('merged_payload', sa.JSON(), nullable=True),
        sa.Column('conflict_type', sa.String(length=50), nullable=False, server_default='CONTENT_CONFLICT'),
        sa.Column('resolution', sa.String(length=50), nullable=False, server_default='USER_REQUIRED'),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('resolved_by_device', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('conflict_id')
    )
    op.create_index('ix_advanced_sync_conflicts_conflict_id', 'advanced_sync_conflicts', ['conflict_id'], unique=True)
    op.create_index('ix_advanced_sync_conflicts_is_resolved', 'advanced_sync_conflicts', ['is_resolved'], unique=False)

    # 6. entity_revisions
    op.create_table(
        'entity_revisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('revision_id', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('snapshot_payload', sa.JSON(), nullable=False),
        sa.Column('change_summary', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('revision_id')
    )
    op.create_index('ix_entity_revisions_revision_id', 'entity_revisions', ['revision_id'], unique=True)
    op.create_index('ix_entity_revisions_version', 'entity_revisions', ['version'], unique=False)

def downgrade() -> None:
    pass
