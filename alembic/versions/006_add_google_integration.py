"""Add Google Drive/Sheets integration fields."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_add_google_integration'
down_revision = '005_add_notifications'
branch_labels = None
depends_on = None

def upgrade():
    # Add Google Drive/Sheets fields to PORF
    op.add_column('porf', sa.Column('spreadsheet_id', sa.String(), nullable=True))
    op.add_column('porf', sa.Column('spreadsheet_url', sa.String(), nullable=True))
    op.add_column('porf', sa.Column('file_id', sa.String(), nullable=True))
    op.add_column('porf', sa.Column('file_url', sa.String(), nullable=True))
    
    # Update PO table to use Google Drive
    op.add_column('po', sa.Column('file_id', sa.String(), nullable=True))
    op.add_column('po', sa.Column('file_url', sa.String(), nullable=True))
    op.drop_column('po', 'pdf_path')

def downgrade():
    # Remove Google Drive/Sheets fields from PORF
    op.drop_column('porf', 'file_url')
    op.drop_column('porf', 'file_id')
    op.drop_column('porf', 'spreadsheet_url')
    op.drop_column('porf', 'spreadsheet_id')
    
    # Restore PO table
    op.add_column('po', sa.Column('pdf_path', sa.String(), nullable=True))
    op.drop_column('po', 'file_url')
    op.drop_column('po', 'file_id') 