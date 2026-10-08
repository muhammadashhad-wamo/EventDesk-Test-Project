"""Add check constraint to ticket count in event

Revision ID: 5f68bb97e55c
Revises: 88f7152815ae
Create Date: 2026-10-08 15:17:17.412355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f68bb97e55c'
down_revision: Union[str, Sequence[str], None] = '88f7152815ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_event_available_tickets_non_negative",
        "event",
        "available_tickets_count >= 0"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_event_available_tickets_non_negative", "event", type_="check")
