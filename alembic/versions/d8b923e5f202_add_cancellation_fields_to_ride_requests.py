"""add cancellation fields to ride_requests

Revision ID: d8b923e5f202
Revises: c7a812d4e101
Create Date: 2026-11-02 12:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8b923e5f202'
down_revision: Union[str, Sequence[str], None] = 'c7a812d4e101'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('ride_requests', sa.Column('cancellation_reason', sa.Text(), nullable=True))
    op.add_column('ride_requests', sa.Column('cancelled_by_id', sa.Integer(), nullable=True))
    op.add_column('ride_requests', sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        'fk_ride_requests_cancelled_by_id_users',
        'ride_requests',
        'users',
        ['cancelled_by_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_ride_requests_cancelled_by_id_users', 'ride_requests', type_='foreignkey')
    op.drop_column('ride_requests', 'cancelled_at')
    op.drop_column('ride_requests', 'cancelled_by_id')
    op.drop_column('ride_requests', 'cancellation_reason')

