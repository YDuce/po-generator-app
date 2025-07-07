from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_channel_folder'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "channel_sheet",
        sa.Column("folder_id", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('channel_sheet', 'folder_id')
