"""add address to user

Revision ID: 335af32e9261
Revises: 25fe7ea5b44b
Create Date: 2023-06-06 19:52:02.836269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '335af32e9261'
down_revision = '25fe7ea5b44b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('address_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'address_users_fk',
        source_table='users',
        referent_table='address',
        local_cols=['address_id'],
        remote_cols=['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    op.drop_constraint('address_users_fk', table_name='users', type_='foreignkey')
    op.drop_column('users', 'address_id')
