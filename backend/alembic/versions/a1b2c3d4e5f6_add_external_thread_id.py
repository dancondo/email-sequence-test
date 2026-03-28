"""add_external_thread_id_to_sequence_run_candidate_event

Revision ID: a1b2c3d4e5f6
Revises: 5e057cad4e8b
Create Date: 2026-03-28 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '5e057cad4e8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'sequence_run_candidate_event',
        sa.Column('external_thread_id', sa.String(), nullable=True),
    )
    op.create_index(
        op.f('ix_sequence_run_candidate_event_external_thread_id'),
        'sequence_run_candidate_event',
        ['external_thread_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_sequence_run_candidate_event_external_thread_id'),
        table_name='sequence_run_candidate_event',
    )
    op.drop_column('sequence_run_candidate_event', 'external_thread_id')
