"""US-021 (część): zabezpieczenia w bazie dla awizacji — jeden kontener raz w awizacji (AvizoItem)
i tylko dozwolone decyzje spedycji (CHECK). Odpowiedzi spedycji (DeliveryConfirmation) celowo NIE są
unikalne: po odrzuceniu spedycja odpowiada ponownie na tę samą awizację.

Migracja NIE usuwa danych. Gdy w bazie są już duplikaty, zatrzymuje się z opisem — najpierw
`python scripts/check_avizo_duplicates.py` (tylko odczyt) i decyzja PO, co zachować.

Revision ID: uniq001
Revises: fikc001
"""
import sqlalchemy as sa
from alembic import op

revision = "uniq001"
down_revision = "fikc001"
branch_labels = None
depends_on = None

# nazwa → (tabela, warunek) — test_db_check_constraints porównuje z modelami
CHECKS = {"ck_avizo_delivery_decision": ("avizo_delivery_confirmations",
                                         "decision IN ('confirmed', 'date_change', 'problem')")}


def _duplicates(table: str) -> int:
    return op.get_bind().execute(sa.text(
        f"SELECT COUNT(*) FROM (SELECT request_id, container_id FROM {table} "   # nosec B608 — stała nazwa tabeli
        "GROUP BY request_id, container_id HAVING COUNT(*) > 1) d")).scalar() or 0


def upgrade() -> None:
    dup = _duplicates("avizo_items")
    bad = op.get_bind().execute(sa.text(
        "SELECT COUNT(*) FROM avizo_delivery_confirmations WHERE NOT ("
        + CHECKS["ck_avizo_delivery_decision"][1] + ")")).scalar() or 0   # nosec B608 — stała
    if dup or bad:
        raise RuntimeError(
            f"uniq001: w bazie są dane sprzeczne z nowymi zabezpieczeniami (duplikaty kontenerów w awizacjach: "
            f"{dup}, złe decyzje: {bad}). "
            "Migracja niczego nie usuwa — uruchom scripts/check_avizo_duplicates.py i ustal z PO, co zachować.")
    with op.batch_alter_table("avizo_items") as batch:
        batch.create_unique_constraint("uq_avizo_items_request_container", ["request_id", "container_id"])
    with op.batch_alter_table("avizo_delivery_confirmations") as batch:
        for name, (_table, sql) in CHECKS.items():
            batch.create_check_constraint(name, sql)


def downgrade() -> None:
    with op.batch_alter_table("avizo_delivery_confirmations") as batch:
        batch.drop_constraint("ck_avizo_delivery_decision", type_="check")
    with op.batch_alter_table("avizo_items") as batch:
        batch.drop_constraint("uq_avizo_items_request_container", type_="unique")
