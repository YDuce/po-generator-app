"""Initial schema + seed org.

Revision ID: 0001_initial
Revises: 
Create Date: 2025-06-13 13:59:00
"""
from __future__ import annotations

from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organisations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("drive_folder_id", sa.String, nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("password_hash", sa.String),
        sa.Column("first_name", sa.String),
        sa.Column("last_name", sa.String),
        sa.Column("google_id", sa.String, unique=True),
        sa.Column(
            "organisation_id",
            sa.Integer,
            sa.ForeignKey("organisations.id"),
            nullable=False,
        ),
    )
    op.create_table(
        "woot_porfs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created_at", sa.DateTime, default=datetime.utcnow),
        sa.Column(
            "updated_at",
            sa.DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
        ),
        sa.Column("porf_no", sa.String, unique=True, nullable=False),
        sa.Column("status", sa.String, nullable=False, default="draft"),
    )
    op.create_table(
        "woot_porf_lines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "porf_id",
            sa.Integer,
            sa.ForeignKey("woot_porfs.id"),
            nullable=False,
        ),
        sa.Column("product_id", sa.String, nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
    )

    org = table(
        "organisations",
        column("id", sa.Integer),
        column("name", sa.String),
        column("drive_folder_id", sa.String),
    )
    op.bulk_insert(
        org,
        [{"id": 1, "name": "default", "drive_folder_id": "SEED-PLACEHOLDER"}],
    )


def downgrade() -> None:
    op.drop_table("woot_porf_lines")
    op.drop_table("woot_porfs")
    op.drop_table("users")
    op.drop_table("organisations")
