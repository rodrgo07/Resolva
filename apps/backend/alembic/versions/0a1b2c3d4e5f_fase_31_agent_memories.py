"""fase_31_agent_memories

Revision ID: 0a1b2c3d4e5f
Revises: 9e0f1a2b3c4d
Create Date: 2026-08-30 00:53:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '9e0f1a2b3c4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'agent_memories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('memory_id', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False, server_default='FACT'),
        sa.Column('content', sa.String(length=1000), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False, server_default='USER_EXPLICIT'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.80'),
        sa.Column('importance', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('memory_id')
    )
    op.create_index('ix_agent_memories_memory_id', 'agent_memories', ['memory_id'], unique=True)
    op.create_index('ix_agent_memories_type', 'agent_memories', ['type'], unique=False)
    op.create_index('ix_agent_memories_status', 'agent_memories', ['status'], unique=False)

def downgrade() -> None:
    pass
