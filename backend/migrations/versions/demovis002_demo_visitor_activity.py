"""Bramka demo: aktywność gościa po wejściu — liczba ekranów, ostatni ekran, sekcje (bez IP).

Revision ID: demovis002
Revises: demovis001
"""
import sqlalchemy as sa
from alembic import op

revision = "demovis002"
down_revision = "demovis001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("demo_visitors", sa.Column("page_views", sa.Integer, nullable=False, server_default="0"))
    op.add_column("demo_visitors", sa.Column("last_seen_at", sa.DateTime, nullable=True))
    op.add_column("demo_visitors", sa.Column("sections", sa.JSON, nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("demo_visitors") as batch:
        batch.drop_column("sections")
        batch.drop_column("last_seen_at")
        batch.drop_column("page_views")
