"""Initial tables

Revision ID: 001_initial
Revises:
Create Date: 2025-07-03
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organisation",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column(
            "drive_folder_id", sa.String(length=256), nullable=False, unique=True
        ),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column(
            "organisation_id",
            sa.Integer(),
            sa.ForeignKey("organisation.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("allowed_channels", sa.JSON(), nullable=True),
    )
    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku", sa.String(length=80), unique=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("listed_date", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "order_record",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.String(length=80), unique=True, nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column(
            "product_sku",
            sa.String(length=80),
            sa.ForeignKey("product.sku"),
            nullable=False,
            index=True,
        ),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("ordered_date", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "insight",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "product_sku",
            sa.String(length=80),
            sa.ForeignKey("product.sku"),
            nullable=False,
            index=True,
        ),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, index=True),
        sa.Column("generated_date", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "reallocation",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "sku",
            sa.String(length=80),
            sa.ForeignKey("product.sku", ondelete="CASCADE"),
            nullable=False,
            index=True,
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
    op.create_table(
        "channel_sheet",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("channel", sa.String(length=50), nullable=False, unique=True),
        sa.Column("spreadsheet_id", sa.String(length=128), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("insight")
    op.drop_table("order_record")
    op.drop_table("user")
    op.drop_table("organisation")
    op.drop_table("reallocation")
    op.drop_table("channel_sheet")
    op.drop_table("product")
