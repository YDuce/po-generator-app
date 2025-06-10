"""add porf status and relationships

Revision ID: 004_add_porf_status_and_relationships
Revises: 001_initial
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "004_add_porf_status_and_relationships"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add organisation_id to users table
    op.add_column('users', sa.Column('organisation_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_users_organisation',
        'users', 'organisations',
        ['organisation_id'], ['id']
    )

    # Add user_id to woot_porfs table
    op.add_column('woot_porfs', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_woot_porfs_user',
        'woot_porfs', 'users',
        ['user_id'], ['id']
    )

    # Add organisation_id to woot_porfs table
    op.add_column('woot_porfs', sa.Column('organisation_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_woot_porfs_organisation',
        'woot_porfs', 'organisations',
        ['organisation_id'], ['id']
    )

    # Add channel_id to woot_porfs table
    op.add_column('woot_porfs', sa.Column('channel_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_woot_porfs_channel',
        'woot_porfs', 'channels',
        ['channel_id'], ['id']
    )


def downgrade() -> None:
    # Remove foreign keys and columns
    op.drop_constraint('fk_woot_porfs_channel', 'woot_porfs', type_='foreignkey')
    op.drop_constraint('fk_woot_porfs_organisation', 'woot_porfs', type_='foreignkey')
    op.drop_constraint('fk_woot_porfs_user', 'woot_porfs', type_='foreignkey')
    op.drop_constraint('fk_users_organisation', 'users', type_='foreignkey')

    op.drop_column('woot_porfs', 'channel_id')
    op.drop_column('woot_porfs', 'organisation_id')
    op.drop_column('woot_porfs', 'user_id')
    op.drop_column('users', 'organisation_id') 