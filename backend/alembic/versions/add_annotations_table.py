"""Add annotations table for article highlighting

Revision ID: c8f9d2a3b5e1
Revises: b2dec15d8292
Create Date: 2025-11-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c8f9d2a3b5e1'
down_revision: Union[str, None] = 'b2dec15d8292'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create annotations table
    op.create_table(
        'annotations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('highlighted_text', sa.Text(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('position_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_annotations_id'), 'annotations', ['id'], unique=False)


def downgrade() -> None:
    # Drop annotations table
    op.drop_index(op.f('ix_annotations_id'), table_name='annotations')
    op.drop_table('annotations')
