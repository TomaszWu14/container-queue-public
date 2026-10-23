"""Bramka demo: tabela demo_visitors (imię, nazwisko, firma, data) — bez IP i user-agenta.

Revision ID: demovis001
Revises: uniq001
"""
import sqlalchemy as sa
from alembic import op

revision = "demovis001"
down_revision = "uniq001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "demo_visitors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("company", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_demo_visitors_created_at", "demo_visitors", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_demo_visitors_created_at", table_name="demo_visitors")
    op.drop_table("demo_visitors")
