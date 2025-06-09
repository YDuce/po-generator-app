"""add organisation table

Revision ID: 009_add_organisation
Revises: 008_add_auth_models
Create Date: 2025-06-09
"""

from alembic import op
import sqlalchemy as sa

revision = "009_add_organisation"
down_revision = "008_add_auth_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organisations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("workspace_folder_id", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("name"),
    )


def downgrade() -> None:
    op.drop_table("organisations")
