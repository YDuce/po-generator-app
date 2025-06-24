"""Add User.allowed_channels column + index."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_add_user_allowed_channels"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "allowed_channels",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.create_index(
        "ix_users_allowed_channels_gin",
        "users",
        ["allowed_channels"],
        postgresql_using="gin",
        postgresql_ops={"allowed_channels": "jsonb_path_ops"},
    )
    op.create_check_constraint(
        "ck_users_allowed_channels_array",
        "users",
        "jsonb_typeof(allowed_channels) = 'array'",
    )


def downgrade() -> None:
    op.drop_index("ix_users_allowed_channels_gin", table_name="users")
    op.drop_column("users", "allowed_channels")
