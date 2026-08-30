"""fase_27_notifications

Revision ID: 7c8e9f1a2b3c
Revises: 26f64fb79e33
Create Date: 2026-08-29 23:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '7c8e9f1a2b3c'
down_revision: Union[str, Sequence[str], None] = '26f64fb79e33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('source', sa.String(length=50), nullable=False, server_default='SYSTEM'))
        batch_op.add_column(sa.Column('source_id', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('dedup_key', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('dismissed_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('scheduled_for', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('expires_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('action_type', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('action_payload', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('requires_confirmation', sa.Boolean(), nullable=False, server_default=sa.text('0')))
        batch_op.add_column(sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'))
        
        batch_op.create_index(batch_op.f('ix_notifications_source'), ['source'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_priority'), ['priority'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_type'), ['type'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_is_read'), ['is_read'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_dedup_key'), ['dedup_key'], unique=False)
        batch_op.create_index('ix_notifications_status_priority', ['status', 'priority'], unique=False)
        batch_op.create_index('ix_notifications_created_at', ['created_at'], unique=False)

def downgrade() -> None:
    pass
