"""
Add name and picture fields to user table
"""

from alembic import op
import sqlalchemy as sa

revision = "003_add_user_profile"
down_revision = "002_auth_tokens"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("name", sa.String(), nullable=True))
    op.add_column("user", sa.Column("picture", sa.String(), nullable=True))


def downgrade():
    op.drop_column("user", "picture")
    op.drop_column("user", "name") 