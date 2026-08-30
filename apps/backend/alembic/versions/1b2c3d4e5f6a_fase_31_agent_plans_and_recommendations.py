"""fase_31_agent_plans_and_recommendations

Revision ID: 1b2c3d4e5f6a
Revises: 0a1b2c3d4e5f
Create Date: 2026-08-30 00:57:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '1b2c3d4e5f6a'
down_revision: Union[str, Sequence[str], None] = '0a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. agent_plans
    op.create_table(
        'agent_plans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('plan_id', sa.String(length=100), nullable=False),
        sa.Column('plan_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PROPOSED'),
        sa.Column('title', sa.String(length=255), nullable=False, server_default='Plano Diário Otimizado'),
        sa.Column('summary', sa.String(length=1000), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plan_id')
    )
    op.create_index('ix_agent_plans_plan_id', 'agent_plans', ['plan_id'], unique=True)
    op.create_index('ix_agent_plans_plan_date', 'agent_plans', ['plan_date'], unique=False)
    op.create_index('ix_agent_plans_status', 'agent_plans', ['status'], unique=False)

    # 2. agent_plan_items
    op.create_table(
        'agent_plan_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.String(length=100), nullable=False),
        sa.Column('time_window', sa.String(length=50), nullable=False),
        sa.Column('activity', sa.String(length=500), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='deep_work'),
        sa.Column('priority_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['plan_id'], ['agent_plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id')
    )
    op.create_index('ix_agent_plan_items_plan_id', 'agent_plan_items', ['plan_id'], unique=False)
    op.create_index('ix_agent_plan_items_item_id', 'agent_plan_items', ['item_id'], unique=True)

    # 3. agent_recommendations
    op.create_table(
        'agent_recommendations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('recommendation_id', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('explanation', sa.String(length=1000), nullable=False),
        sa.Column('why_reason', sa.String(length=500), nullable=False),
        sa.Column('based_on', sa.String(length=500), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.85'),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='medium'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('suggested_actions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recommendation_id')
    )
    op.create_index('ix_agent_recommendations_recommendation_id', 'agent_recommendations', ['recommendation_id'], unique=True)
    op.create_index('ix_agent_recommendations_category', 'agent_recommendations', ['category'], unique=False)

    # 4. agent_recommendation_feedbacks
    op.create_table(
        'agent_recommendation_feedbacks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('recommendation_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACCEPTED'),
        sa.Column('user_comment', sa.String(length=500), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['recommendation_id'], ['agent_recommendations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_recommendation_feedbacks_recommendation_id', 'agent_recommendation_feedbacks', ['recommendation_id'], unique=False)

def downgrade() -> None:
    pass
