"""add_status_column_to_rides_table

Revision ID: 75c90c7f52d0
Revises: b121a87b0e26
Create Date: 2026-08-25 14:00:59.224504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75c90c7f52d0'
down_revision: Union[str, Sequence[str], None] = 'b121a87b0e26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'rides',
        sa.Column(
            'status',
            sa.String(length=30),
            nullable=False,
            server_default='CREATED'
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('rides', 'status')

