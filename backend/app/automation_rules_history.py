"""Historia zmian reguł z kreatora i „przywróć stan sprzed zmiany” (trzecia lista PO, pkt 4).

Źródło: dziennik zmian (`AuditLog`, entity_type „automation_rule”) — zapis reguł już zostawia tam osobny
wpis na każdą dodaną, zmienioną i usuniętą regułę (stan przed i po jako JSON). Bez nowej tabeli.
Przywrócenie dotyczy jednej reguły: wraca jej stan sprzed wybranej zmiany (dodanie → reguła znika,
usunięcie → wraca, zmiana → poprzednie ustawienia); reszta listy zostaje bez zmian."""
from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from . import automation_rules as rules_engine
from .models import AuditLog

ENTITY = "automation_rule"
HISTORY_LIMIT = 50
FIELDS = ("name", "enabled", "condition", "days", "status", "notify", "channels")


def _rule(raw: str | None) -> dict | None:
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def history(db: Session, limit: int = HISTORY_LIMIT) -> list[dict]:
    rows = db.scalars(select(AuditLog).options(selectinload(AuditLog.user))
                      .where(AuditLog.entity_type == ENTITY)
                      .order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).limit(limit)).all()
    out = []
    for row in rows:
        old, new = _rule(row.old_value), _rule(row.new_value)
        action = "added" if old is None else "removed" if new is None else "changed"
        changed = [f for f in FIELDS if (old or {}).get(f) != (new or {}).get(f)] if action == "changed" else []
        out.append({"id": row.id, "at": row.created_at.isoformat(), "action": action,
                    "user": (row.user.full_name or row.user.login) if row.user else "",
                    "name": (new or old or {}).get("name", ""), "changed": changed,
                    "before": old, "after": new, "note": row.note})
    return out


def restore(db: Session, audit_id: int) -> tuple[list[rules_engine.Rule], dict | None, dict | None]:
    """Stan reguły sprzed wpisu `audit_id` → nowa lista reguł (zapis i audyt robi wywołujący).
    Zwraca (lista, stan_przed_przywróceniem, stan_po)."""
    row = db.get(AuditLog, audit_id)
    if row is None or row.entity_type != ENTITY or not row.field.startswith("rule."):
        raise LookupError("Nie ma takiego wpisu w historii reguł.")
    rule_id = row.field.removeprefix("rule.")
    target = _rule(row.old_value)
    current = rules_engine.load(db)
    now = next((r for r in current if r.id == rule_id), None)
    rest = [r for r in current if r.id != rule_id]
    if target is None:
        return rest, now.model_dump(mode="json") if now else None, None
    restored = rules_engine.Rule.model_validate({**target, "id": rule_id})
    rules = [restored if r.id == rule_id else r for r in current] if now else [*current, restored]
    return rules, now.model_dump(mode="json") if now else None, restored.model_dump(mode="json")
