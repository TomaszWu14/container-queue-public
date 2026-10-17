"""Fikcyjne nazwy: magazyn DLT → MAG-1, spółki Borealis → Beta, Cobalt Sport → Gamma,
Iberia (PT) → Delta. Tabela dlt_stock → mag1_stock, status wyslane_z_dlt → wyslane_z_mag1.

Revision ID: fikc001
Revises: mailin001
"""
from alembic import op

revision = "fikc001"
down_revision = "mailin001"
branch_labels = None
depends_on = None

# (stara wartość, nowa) — nazwa spółki, kod spółki, nazwa magazynu
COMPANY_NAMES = [("Borealis", "Beta"), ("Cobalt Sport", "Gamma"), ("Iberia", "Delta")]
COMPANY_CODES = [("BOREALIS", "BETA"), ("COBALT", "GAMMA"), ("PT", "DELTA")]
WAREHOUSES = [("DLT", "MAG-1"), ("BOREALIS", "BETA"), ("COBALTSPORT", "GAMMA"), ("IBERIA", "DELTA")]


def _swap(pairs: list[tuple[str, str]], reverse: bool) -> list[tuple[str, str]]:
    return [(new, old) for old, new in pairs] if reverse else pairs


def _rename(reverse: bool) -> None:
    pg = op.get_bind().dialect.name == "postgresql"
    old_t, new_t = ("mag1_stock", "dlt_stock") if reverse else ("dlt_stock", "mag1_stock")
    op.rename_table(old_t, new_t)
    op.execute(f"ALTER INDEX ix_{old_t}_produkt RENAME TO ix_{new_t}_produkt" if pg
               else f"DROP INDEX IF EXISTS ix_{old_t}_produkt")
    if pg:   # klucz główny i sekwencja id zachowują starą nazwę po RENAME TABLE
        op.execute(f"ALTER TABLE {new_t} RENAME CONSTRAINT {old_t}_pkey TO {new_t}_pkey")
        op.execute(f"ALTER SEQUENCE IF EXISTS {old_t}_id_seq RENAME TO {new_t}_id_seq")
    else:
        op.create_index(f"ix_{new_t}_produkt", new_t, ["produkt"])

    old_s, new_s = ("wyslane_z_mag1", "wyslane_z_dlt") if reverse else ("wyslane_z_dlt", "wyslane_z_mag1")
    if pg:   # PostgreSQL 10+: zmiana nazwy wartości enuma przenosi też istniejące wiersze
        op.execute(f"ALTER TYPE palletcallstatus RENAME VALUE '{old_s}' TO '{new_s}'")
    else:    # SQLite trzyma enum jako tekst
        op.execute(f"UPDATE pallet_calls SET status = '{new_s}' WHERE status = '{old_s}'")

    for old, new in _swap(COMPANY_NAMES, reverse):
        op.execute(f"UPDATE companies SET name = '{new}' WHERE name = '{old}'")
    for old, new in _swap(COMPANY_CODES, reverse):
        op.execute(f"UPDATE companies SET code = '{new}' WHERE code = '{old}'")
        op.execute(f"UPDATE material_issues SET firma = '{new}' WHERE firma = '{old}'")
    for old, new in _swap(WAREHOUSES, reverse):
        op.execute(f"UPDATE warehouses SET name = '{new}' WHERE name = '{old}'")


def upgrade() -> None:
    _rename(reverse=False)


def downgrade() -> None:
    _rename(reverse=True)
