"""add apartment number column

Revision ID: c826c4a6d09e
Revises: 335af32e9261
Create Date: 2023-06-08 10:30:13.447733

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c826c4a6d09e'
down_revision = '335af32e9261'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('address', sa.Column('apartment_number', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('address', 'apartment_number')
