"""Add notifications table."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_add_notifications'
down_revision = '004_add_porf_status_and_relationships'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_user_id'), 'notification', ['user_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_notification_user_id'), table_name='notification')
    op.drop_table('notification') 