"""add woot batch and batchline tables

Revision ID: 0e372f80175a
Revises: 61ed1babad18
Create Date: 2025-05-25 19:19:05.418386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e372f80175a'
down_revision: Union[str, None] = '61ed1babad18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'woot_batch',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    op.create_table(
        'woot_batch_line',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('batch_id', sa.Integer, sa.ForeignKey('woot_batch.id'), nullable=False),
        sa.Column('listing_id', sa.Integer, sa.ForeignKey('listing.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('woot_batch_line')
    op.drop_table('woot_batch')
