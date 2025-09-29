"""add horse_market_listings table

Revision ID: a65a9d322676
Revises: 31a31f3b8b6d
Create Date: 2025-06-25 14:21:06.879325
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a65a9d322676'
down_revision = '31a31f3b8b6d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'horse_market_listings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('horse_id', sa.Integer(), sa.ForeignKey('horses.id'), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean(), server_default=sa.sql.expression.true(), nullable=False),
    )


def downgrade():
    op.drop_table('horse_market_listings')
