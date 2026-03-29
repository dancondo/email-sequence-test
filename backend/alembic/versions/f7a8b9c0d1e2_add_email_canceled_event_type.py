"""add_email_canceled_event_type

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-03-29 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, None] = "e6f7a8b9c0d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'EMAIL_CANCELED'")


def downgrade() -> None:
    # PostgreSQL does not support removing values from an enum type.
    pass
