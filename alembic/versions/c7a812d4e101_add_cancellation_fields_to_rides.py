"""add cancellation fields to rides

Revision ID: c7a812d4e101
Revises: 94e24029fcfd
Create Date: 2026-11-02 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7a812d4e101'
down_revision: Union[str, Sequence[str], None] = '94e24029fcfd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('rides', sa.Column('cancellation_reason', sa.Text(), nullable=True))
    op.add_column('rides', sa.Column('cancelled_by_id', sa.Integer(), nullable=True))
    op.add_column('rides', sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        'fk_rides_cancelled_by_id_users',
        'rides',
        'users',
        ['cancelled_by_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_rides_cancelled_by_id_users', 'rides', type_='foreignkey')
    op.drop_column('rides', 'cancelled_at')
    op.drop_column('rides', 'cancelled_by_id')
    op.drop_column('rides', 'cancellation_reason')

