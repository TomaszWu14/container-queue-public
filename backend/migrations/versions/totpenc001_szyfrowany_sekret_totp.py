"""Sekret TOTP szyfrowany w bazie (ASVS 2.8.2, US-092, decyzja PO 2026-10-19).

Kolumna users.totp_secret VARCHAR(64) → VARCHAR(255) (szyfrogram Fernet ma ~145 znaków) i
szyfrowanie istniejących jawnych sekretów tym samym kluczem co reszta danych (app.crypto,
DATA_ENCRYPTION_KEY). Niczego nie usuwa. Cofnięcie odszyfrowuje i zwęża kolumnę.

Revision ID: totpenc001
Revises: fikc001
"""
import sqlalchemy as sa
from alembic import op

from app import crypto

revision = "totpenc001"
down_revision = "fikc001"
branch_labels = None
depends_on = None


def _rows(conn) -> list[tuple[int, str]]:
    return [(r[0], r[1]) for r in conn.execute(
        sa.text("SELECT id, totp_secret FROM users WHERE totp_secret IS NOT NULL AND totp_secret <> ''"))]


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":      # SQLite nie pilnuje długości VARCHAR
        op.alter_column("users", "totp_secret", existing_type=sa.String(64),
                        type_=sa.String(255), existing_nullable=True)
    for uid, secret in _rows(conn):
        if not secret.startswith("enc:"):
            conn.execute(sa.text("UPDATE users SET totp_secret = :s WHERE id = :i"),
                         {"s": crypto.encrypt(secret), "i": uid})


def downgrade() -> None:
    conn = op.get_bind()
    for uid, secret in _rows(conn):
        if secret.startswith("enc:"):
            conn.execute(sa.text("UPDATE users SET totp_secret = :s WHERE id = :i"),
                         {"s": crypto.decrypt(secret), "i": uid})
    if conn.dialect.name == "postgresql":
        op.alter_column("users", "totp_secret", existing_type=sa.String(255),
                        type_=sa.String(64), existing_nullable=True)
