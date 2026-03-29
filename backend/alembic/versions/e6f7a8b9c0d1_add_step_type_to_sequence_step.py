"""add_step_type_to_sequence_step

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-03-29 22:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e6f7a8b9c0d1"
down_revision: Union[str, None] = "d5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create step_type enum
    steptype = sa.Enum("default", "referral_handoff", name="steptype")
    steptype.create(op.get_bind(), checkfirst=True)

    # Add step_type column to sequence_step
    op.add_column(
        "sequence_step",
        sa.Column(
            "step_type",
            steptype,
            nullable=False,
            server_default="default",
        ),
    )

    # Add REFERRAL_HANDOFF_SENT to eventtype enum (uppercase to match existing convention)
    op.execute(
        "ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'REFERRAL_HANDOFF_SENT'"
    )


def downgrade() -> None:
    op.drop_column("sequence_step", "step_type")
    sa.Enum(name="steptype").drop(op.get_bind(), checkfirst=True)
    # PostgreSQL does not support removing values from an enum type.
