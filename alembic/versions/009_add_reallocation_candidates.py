"""Add reallocation candidates table."""

import sqlalchemy as sa

from alembic import op

revision = "009_add_reallocation_candidates"
down_revision = "008_add_auth_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reallocation_candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("from_channel", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["master_products.id"], ondelete="CASCADE"
        ),
    )


def downgrade() -> None:
    op.drop_table("reallocation_candidates")
