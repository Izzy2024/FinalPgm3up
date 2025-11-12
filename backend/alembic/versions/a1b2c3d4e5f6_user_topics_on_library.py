"""Add user_topics to user_libraries and improve idempotency

Revision ID: a1b2c3d4e5f6
Revises: f3d9c1a0e123
Create Date: 2025-11-11 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f3d9c1a0e123"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Add user_topics array column if missing
    cols = {c['name'] for c in inspector.get_columns('user_libraries')}
    if 'user_topics' not in cols:
        op.add_column(
            'user_libraries',
            sa.Column('user_topics', postgresql.ARRAY(sa.String()), nullable=True)
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c['name'] for c in inspector.get_columns('user_libraries')}
    if 'user_topics' in cols:
        op.drop_column('user_libraries', 'user_topics')

