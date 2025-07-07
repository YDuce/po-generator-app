"""Add organisation_id to channel sheet"""

from alembic import op
import sqlalchemy as sa

revision = '003_channelsheet_org'
down_revision = '002_channel_folder'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("channel_sheet") as batch:
        batch.add_column(sa.Column("organisation_id", sa.Integer(), nullable=False))
        batch.create_foreign_key(
            "fk_channel_sheet_org",
            "organisation",
            ["organisation_id"],
            ["id"],
        )
        batch.create_index(
            "ix_channel_sheet_organisation_id",
            ["organisation_id"],
        )
        batch.create_unique_constraint(
            "uq_org_channel",
            ["organisation_id", "channel"],
        )


def downgrade() -> None:
    with op.batch_alter_table('channel_sheet') as batch:
        batch.drop_constraint('uq_org_channel', type_='unique')
        batch.drop_index('ix_channel_sheet_organisation_id')
        batch.drop_constraint('fk_channel_sheet_org', type_='foreignkey')
        batch.drop_column('organisation_id')
