"""create_email_account_table

Revision ID: 2aa70fdfd8b9
Revises:
Create Date: 2026-03-28 15:37:34.608461

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2aa70fdfd8b9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


email_provider_enum = sa.Enum('GOOGLE', 'MICROSOFT', name='emailprovider')
integration_provider_enum = sa.Enum('NYLAS', name='integrationprovider')


def upgrade() -> None:
    op.create_table('email_account',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('grant_id', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('provider', email_provider_enum, nullable=False),
    sa.Column('integration_provider', integration_provider_enum, nullable=False),
    sa.Column('connected_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('grant_id')
    )


def downgrade() -> None:
    op.drop_table('email_account')
    email_provider_enum.drop(op.get_bind(), checkfirst=True)
    integration_provider_enum.drop(op.get_bind(), checkfirst=True)
