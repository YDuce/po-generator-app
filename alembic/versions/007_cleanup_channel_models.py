"""Clean up channel models and tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_cleanup_channel_models'
down_revision = '006_add_google_integration'
branch_labels = None
depends_on = None

def upgrade():
    # Create Woot-specific tables
    op.create_table(
        'woot_porf',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('porf_no', sa.String(50), nullable=False),
        sa.Column('status', sa.Enum('draft', 'approved', 'expired', name='porfstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('total_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('spreadsheet_id', sa.String(), nullable=True),
        sa.Column('spreadsheet_url', sa.String(), nullable=True),
        sa.Column('file_id', sa.String(), nullable=True),
        sa.Column('file_url', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('porf_no')
    )
    
    op.create_table(
        'woot_po',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('po_no', sa.String(50), nullable=False),
        sa.Column('porf_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('open', 'expired', name='postatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('ship_by', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_ordered', sa.Numeric(12, 2), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('file_id', sa.String(), nullable=True),
        sa.Column('file_url', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['porf_id'], ['woot_porf.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('po_no')
    )
    
    op.create_table(
        'woot_porf_line',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('porf_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('qty', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('extra', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['porf_id'], ['woot_porf.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'woot_po_line',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('po_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(50), nullable=False),
        sa.Column('ordered_qty', sa.Integer(), nullable=False),
        sa.Column('remaining_qty', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('extra', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['po_id'], ['woot_po.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Drop old tables
    op.drop_table('porf_line')
    op.drop_table('po')
    op.drop_table('porf')

def downgrade():
    # Recreate old tables
    op.create_table(
        'porf',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('porf_no', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('porf_no')
    )
    
    op.create_table(
        'po',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('po_no', sa.String(), nullable=False),
        sa.Column('porf_id', sa.Integer(), nullable=False),
        sa.Column('pdf_path', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['porf_id'], ['porf.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('po_no')
    )
    
    op.create_table(
        'porf_line',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('porf_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('qty', sa.Integer(), nullable=False),
        sa.Column('line_json', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['porf_id'], ['porf.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Drop new tables
    op.drop_table('woot_po_line')
    op.drop_table('woot_porf_line')
    op.drop_table('woot_po')
    op.drop_table('woot_porf') 