"""Add reallocation table

Revision ID: 002_reallocation
Revises: 001_initial
Create Date: 2025-07-03
"""

from alembic import op
import sqlalchemy as sa

revision = "002_reallocation"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reallocation",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "sku",
            sa.String(length=80),
            sa.ForeignKey("product.sku", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel_origin", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column(
            "added_date",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "sku", "channel_origin", "reason", name="uq_reallocation_sku_chan_reason"
        ),
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_reallocation_sku_chan_reason",
        "reallocation",
        type_="unique",
    )
    op.drop_table("reallocation")
