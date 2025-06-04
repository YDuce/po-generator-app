"""
Add user and oauth_token tables for Woot-MVP v2.4
"""
from alembic import op
import sqlalchemy as sa
import os
from passlib.hash import bcrypt

revision = '002_auth_tokens'
down_revision = '001_category_status'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('password_hash', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        'oauth_token',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('provider', sa.String, nullable=False),
        sa.Column('access_token', sa.String, nullable=False),
        sa.Column('refresh_token', sa.String, nullable=True),
        sa.Column('expires_at', sa.DateTime, nullable=True),
    )
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_pw = os.getenv('ADMIN_PASSWORD', 'admin')
    if admin_email:
        pw_hash = bcrypt.hash(admin_pw)
        op.execute(
            sa.text("""
                INSERT INTO "user" (email, password_hash, created_at)
                VALUES (:email, :pw_hash, CURRENT_TIMESTAMP)
            """).bindparams(email=admin_email, pw_hash=pw_hash)
        )

def downgrade():
    op.drop_table('oauth_token')
    op.drop_table('user') 