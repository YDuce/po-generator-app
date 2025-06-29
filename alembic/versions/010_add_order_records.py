"""add order_records and order_lines"""

import sqlalchemy as sa

from alembic import op

revision = "010_add_order_records"
down_revision = "009_add_reallocation_candidates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "order_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ext_id", sa.String(length=50), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "currency", sa.String(length=3), nullable=False, server_default="USD"
        ),
        sa.Column("total", sa.String(length=20), nullable=False),
        sa.Column("placed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(op.f("ix_order_records_ext_id"), "order_records", ["ext_id"])

    op.create_table(
        "order_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("order_records.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("order_lines")
    op.drop_table("order_records")
