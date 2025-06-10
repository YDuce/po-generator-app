"""
Migration for Woot-MVP v2.3: category, status enums, and all required tables.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_category_status"
down_revision = "000_init_woot_mvp"
branch_labels = None
depends_on = None


def upgrade():
    # Enums (Postgres only)
    if op.get_context().dialect.name == "postgresql":
        op.execute(
            """
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'porfstatus') THEN
                CREATE TYPE porfstatus AS ENUM ('draft', 'approved', 'expired');
            END IF;
        END$$;
        """
        )
        op.execute(
            """
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'postatus') THEN
                CREATE TYPE postatus AS ENUM ('open', 'expired');
            END IF;
        END$$;
        """
        )
        porf_status_type = postgresql.ENUM(
            "draft", "approved", "expired", name="porfstatus", create_type=False
        )
        po_status_type = postgresql.ENUM(
            "open", "expired", name="postatus", create_type=False
        )
    else:
        porf_status_type = sa.String(16)
        po_status_type = sa.String(16)

    op.create_table(
        "category",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("path", sa.String, nullable=False),
        sa.Column("family", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=False),
        sa.Column(
            "is_custom", sa.Boolean, nullable=False, server_default=sa.text("false")
        ),
    )
    op.create_table(
        "product",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("sku", sa.String, unique=True, nullable=False),
        sa.Column("asin", sa.String, nullable=True),
        sa.Column("fnsku", sa.String, nullable=True),
        sa.Column("core_attrs", sa.JSON, nullable=True),
    )
    op.create_table(
        "product_category",
        sa.Column(
            "product_id", sa.Integer, sa.ForeignKey("product.id"), primary_key=True
        ),
        sa.Column(
            "category_id", sa.Integer, sa.ForeignKey("category.id"), primary_key=True
        ),
    )
    op.create_index(
        "ix_product_category_category_id_product_id",
        "product_category",
        ["category_id", "product_id"],
    )
    op.create_table(
        "porf",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("porf_no", sa.String, nullable=False),
        sa.Column("status", porf_status_type, nullable=False),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_table(
        "po",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("po_no", sa.String, nullable=False),
        sa.Column("win_no", sa.String, nullable=False),
        sa.Column("porf_id", sa.Integer, sa.ForeignKey("porf.id"), nullable=False),
        sa.Column("status", po_status_type, nullable=False),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("pdf_path", sa.String, nullable=True),
    )
    op.create_table(
        "porf_line",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("porf_id", sa.Integer, sa.ForeignKey("porf.id"), nullable=False),
        sa.Column(
            "product_id", sa.Integer, sa.ForeignKey("product.id"), nullable=False
        ),
        sa.Column("qty", sa.Integer, nullable=False),
        sa.Column("line_json", sa.JSON, nullable=True),
    )
    op.create_table(
        "event_uploader",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("porf_id", sa.Integer, sa.ForeignKey("porf.id"), nullable=False),
        sa.Column(
            "category_id", sa.Integer, sa.ForeignKey("category.id"), nullable=False
        ),
        sa.Column("file_path", sa.String, nullable=False),
        sa.Column(
            "uploaded_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_table(
        "inventory_record",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "product_id", sa.Integer, sa.ForeignKey("product.id"), nullable=False
        ),
        sa.Column("channel_id", sa.Integer, nullable=False),
        sa.Column("delta", sa.Integer, nullable=False),
        sa.Column(
            "recorded_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade():
    op.drop_table("inventory_record")
    op.drop_table("event_uploader")
    op.drop_table("porf_line")
    op.drop_table("po")
    op.drop_table("porf")
    op.drop_index(
        "ix_product_category_category_id_product_id", table_name="product_category"
    )
    op.drop_table("product_category")
    op.drop_table("product")
    op.drop_table("category")
    if op.get_context().dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS porfstatus")
        op.execute("DROP TYPE IF EXISTS postatus")
