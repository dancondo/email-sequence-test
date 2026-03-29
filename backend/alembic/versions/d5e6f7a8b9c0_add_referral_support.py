"""add_referral_support

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-03-29 20:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add referred_by_candidate_id to candidate table (self-referencing FK)
    op.add_column(
        "candidate",
        sa.Column(
            "referred_by_candidate_id",
            sa.Integer(),
            sa.ForeignKey("candidate.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # Add referral_list_id to sequence table
    op.add_column(
        "sequence",
        sa.Column(
            "referral_list_id",
            sa.Integer(),
            sa.ForeignKey("candidate_list.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # Add referral_detected to eventtype enum
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'REFERRAL_DETECTED'")


def downgrade() -> None:
    op.drop_column("sequence", "referral_list_id")
    op.drop_column("candidate", "referred_by_candidate_id")
    # PostgreSQL does not support removing values from an enum type.
