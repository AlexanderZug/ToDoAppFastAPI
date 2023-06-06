"""phone num for user table

Revision ID: c96fb23c0164
Revises: 
Create Date: 2023-06-06 19:24:48.487363

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c96fb23c0164'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
