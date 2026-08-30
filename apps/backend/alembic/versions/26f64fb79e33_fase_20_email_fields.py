"""fase_20_email_fields

Revision ID: 26f64fb79e33
Revises: 63ed54c28728
Create Date: 2026-08-29 22:10:28.694430

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

revision: str = '26f64fb79e33'
down_revision: Union[str, Sequence[str], None] = '63ed54c28728'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    with op.batch_alter_table('email_accounts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sync_status', sa.String(length=50), nullable=False, server_default='idle'))
        batch_op.add_column(sa.Column('sync_error', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('next_page_token', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('history_id', sa.String(length=255), nullable=True))
        batch_op.alter_column('credentials_encrypted', existing_type=sqlite.JSON(), nullable=True)
        batch_op.create_index(batch_op.f('ix_email_accounts_email_address'), ['email_address'], unique=False)
        batch_op.create_index(batch_op.f('ix_email_accounts_provider'), ['provider'], unique=False)

    with op.batch_alter_table('emails', schema=None) as batch_op:
        batch_op.add_column(sa.Column('thread_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('to_addresses', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('body_text', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('body_html', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('is_starred', sa.Boolean(), nullable=False, server_default=sa.text('0')))
        batch_op.add_column(sa.Column('is_important', sa.Boolean(), nullable=False, server_default=sa.text('0')))
        batch_op.add_column(sa.Column('labels', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('ai_reasoning', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('synced_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        batch_op.alter_column('subject', existing_type=sa.VARCHAR(length=255), type_=sa.String(length=500), existing_nullable=False)
        batch_op.alter_column('ai_classification', existing_type=sa.VARCHAR(length=100), type_=sa.String(length=50), existing_nullable=True)
        batch_op.create_index('ix_emails_account_external', ['account_id', 'external_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_emails_account_id'), ['account_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_emails_ai_classification'), ['ai_classification'], unique=False)
        batch_op.create_index(batch_op.f('ix_emails_external_id'), ['external_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_emails_from_address'), ['from_address'], unique=False)
        batch_op.create_index(batch_op.f('ix_emails_is_read'), ['is_read'], unique=False)
        batch_op.create_index(batch_op.f('ix_emails_needs_reply'), ['needs_reply'], unique=False)
        batch_op.create_index(batch_op.f('ix_emails_received_at'), ['received_at'], unique=False)
        batch_op.create_index('ix_emails_received_read', ['received_at', 'is_read'], unique=False)
        batch_op.create_index(batch_op.f('ix_emails_thread_id'), ['thread_id'], unique=False)

def downgrade() -> None:
    pass
