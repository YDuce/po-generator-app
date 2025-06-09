"""Consolidated authentication models migration.

This migration consolidates the authentication-related schema changes from previous
migrations (008 and 009) into a single, clean migration. It includes:

1. User Table Enhancements:
   - Added is_active flag for user account status
   - Added updated_at timestamp for tracking modifications
   - Added company_name for organization identification
   - Added company_address for business location
   - Added phone for contact information

2. OAuth Tokens Table:
   - Stores OAuth tokens for external service integration
   - Links tokens to users via user_id foreign key
   - Tracks token expiration and refresh capabilities
   - Includes created_at and updated_at timestamps

3. Sessions Table:
   - Manages user session information
   - Stores JWT tokens with expiration
   - Tracks last activity for session management
   - Includes created_at and updated_at timestamps
   - Enforces unique token constraint

The migration is designed to be reversible, with proper downgrade paths for all
changes. It maintains referential integrity through foreign key constraints.

Revision ID: 008
Revises: 005_add_notifications
Create Date: 2024-03-19 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '005_add_notifications'
branch_labels = None
depends_on = None

def upgrade():
    """Apply the migration changes.
    
    This function:
    1. Adds new columns to the users table
    2. Creates the oauth_tokens table
    3. Creates the sessions table
    
    All changes are made with proper foreign key constraints and indexes.
    """
    # Add new columns to users table
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('users', sa.Column('company_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('company_address', sa.String(), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))
    
    # Create oauth_tokens table
    op.create_table(
        'oauth_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('service', sa.String(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

def downgrade():
    """Reverse the migration changes.
    
    This function:
    1. Drops the sessions table
    2. Drops the oauth_tokens table
    3. Removes the new columns from the users table
    
    Changes are reversed in the correct order to maintain referential integrity.
    """
    # Drop tables in reverse order
    op.drop_table('sessions')
    op.drop_table('oauth_tokens')
    
    # Drop columns from users table
    op.drop_column('users', 'phone')
    op.drop_column('users', 'company_address')
    op.drop_column('users', 'company_name')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'is_active') 