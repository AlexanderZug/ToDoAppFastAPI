"""create address table

Revision ID: 25fe7ea5b44b
Revises: c96fb23c0164
Create Date: 2023-06-06 19:37:08.564641

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25fe7ea5b44b'
down_revision = 'c96fb23c0164'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'address',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('street', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=255), nullable=False),
        sa.Column('state', sa.String(length=255), nullable=False),
        sa.Column('country', sa.String(length=255), nullable=False),
        sa.Column('postal_code', sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('address')
