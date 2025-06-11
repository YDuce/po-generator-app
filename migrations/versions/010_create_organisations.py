"""
Revision ID: 010_create_organisations
Revises: 009_update_auth_models
Create Date: 2024-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '010_create_organisations'
down_revision = '009_update_auth_models'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'organisations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('drive_folder_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

def downgrade():
    op.drop_table('organisations')
