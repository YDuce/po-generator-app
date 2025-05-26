"""init_woot_mvp

Revision ID: a1b2c3d4e5f6
Revises: da25644e7cda
Create Date: 2024-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'da25644e7cda'
branch_labels = None
depends_on = None

def upgrade():
    # -- Product additions
    op.add_column('product', sa.Column('core_attrs', sa.JSON(), nullable=True))

    # -- New tables
    op.create_table(
        'porf',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('porf_no', sa.String(), nullable=False, unique=True),
        sa.Column('status', sa.String(), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'porf_line',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('porf_id', sa.Integer(), sa.ForeignKey('porf.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('product.id'), nullable=False),
        sa.Column('qty', sa.Integer(), nullable=False),
        sa.Column('extra', sa.JSON(), nullable=True),
    )

    op.create_table(
        'po',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('po_no', sa.String(), unique=True, nullable=False),
        sa.Column('porf_id', sa.Integer(), sa.ForeignKey('porf.id'), nullable=False),
        sa.Column('pdf_path', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
    )

    # -- inventory_record modifications
    with op.batch_alter_table('inventory_record', schema=None) as batch_op:
        if 'quantity' in [c.name for c in batch_op.get_columns()]:
            batch_op.alter_column('quantity', new_column_name='delta')
        batch_op.add_column(sa.Column('product_id', sa.Integer(), sa.ForeignKey('product.id'), nullable=True))
        batch_op.add_column(sa.Column('channel_id', sa.Integer(), sa.ForeignKey('channel.id'), nullable=True))
        batch_op.add_column(sa.Column('source', sa.String(), nullable=True))


def downgrade():
    op.drop_table('po')
    op.drop_table('porf_line')
    op.drop_table('porf')
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('core_attrs')
    # Note: inventory_record downgrade omitted for brevity 