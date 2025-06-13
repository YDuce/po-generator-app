"""Placeholder migration to maintain linear history.

Revision ID: 004_placeholder
Revises: 001_initial
Create Date: 2024-03-19 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "004_placeholder"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op upgrade."""
    pass


def downgrade() -> None:
    """No-op downgrade."""
    pass
