"""Add auto topics to articles and user indexes table

Revision ID: f3d9c1a0e123
Revises: c8f9d2a3b5e1
Create Date: 2025-11-11 04:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "f3d9c1a0e123"
down_revision: Union[str, None] = "c8f9d2a3b5e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Add column articles.auto_topics if it doesn't exist
    article_columns = {col['name'] for col in inspector.get_columns('articles')}
    if 'auto_topics' not in article_columns:
        op.add_column(
            "articles",
            sa.Column(
                "auto_topics",
                postgresql.ARRAY(sa.String()),
                nullable=True,
                server_default="{}",
            ),
        )

    # Create table user_indexes if it doesn't exist
    if not inspector.has_table('user_indexes'):
        op.create_table(
            "user_indexes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column(
                "keywords",
                postgresql.ARRAY(sa.String()),
                nullable=False,
                server_default="{}",
            ),
            sa.Column("color", sa.String(length=20), nullable=True, server_default="#2563eb"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    # Create indexes if missing
    existing_indexes = {idx['name'] for idx in inspector.get_indexes('user_indexes')}
    if op.f("ix_user_indexes_id") not in existing_indexes:
        op.create_index(op.f("ix_user_indexes_id"), "user_indexes", ["id"], unique=False)
    if op.f("ix_user_indexes_user_id") not in existing_indexes:
        op.create_index(op.f("ix_user_indexes_user_id"), "user_indexes", ["user_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Drop indexes if they exist
    if inspector.has_table('user_indexes'):
        existing_indexes = {idx['name'] for idx in inspector.get_indexes('user_indexes')}
        if op.f("ix_user_indexes_user_id") in existing_indexes:
            op.drop_index(op.f("ix_user_indexes_user_id"), table_name="user_indexes")
        if op.f("ix_user_indexes_id") in existing_indexes:
            op.drop_index(op.f("ix_user_indexes_id"), table_name="user_indexes")
        op.drop_table("user_indexes")

    # Drop column if it exists
    article_columns = {col['name'] for col in inspector.get_columns('articles')}
    if 'auto_topics' in article_columns:
        op.drop_column("articles", "auto_topics")
