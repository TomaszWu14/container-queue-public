"""Kreator reguł bez kodu (US-036): lista reguł, zapis (admin, z audytem) i podgląd „ile kontenerów
spełnia regułę dziś” w zakresie użytkownika. Logika warunków: `app/automation_rules.py`."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import automation_rules as rules_engine
from ..audit import record
from ..database import get_db
from ..deps import AdminOnly as admin_only
from ..deps import Editors as editors
from ..deps import scope_containers
from ..models import Container, ContainerStatus, User, today_pl, utcnow

router = APIRouter(prefix="/api", tags=["automations"])
PREVIEW_SAMPLE = 10


class RulesIn(BaseModel):
    rules: list[rules_engine.Rule]


def _out(rules: list[rules_engine.Rule]) -> dict:
    return {"rules": [r.model_dump(mode="json") for r in rules],
            "conditions": list(rules_engine.CONDITIONS), "channels": list(rules_engine.CHANNELS),
            "statuses": [s.value for s in ContainerStatus], "max_rules": rules_engine.MAX_RULES}


@router.get("/automations/rules")
def list_rules(db: Session = Depends(get_db), user: User = editors) -> dict:
    return _out(rules_engine.load(db))


@router.put("/automations/rules")
def save_rules(body: RulesIn, db: Session = Depends(get_db), user: User = admin_only) -> dict:
    before = {r.id: r for r in rules_engine.load(db)}
    try:
        saved = rules_engine.save(db, body.rules)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    after = {r.id: r for r in saved}
    # audyt: każda dodana, zmieniona i usunięta reguła osobno (kto, kiedy, co)
    for rule_id in sorted(set(before) | set(after)):
        old, new = before.get(rule_id), after.get(rule_id)
        if old == new:
            continue
        record(db, entity_type="automation_rule", entity_id=0, field=f"rule.{rule_id}",
               old_value=old.model_dump_json() if old else None,
               new_value=new.model_dump_json() if new else None, user=user)
    db.commit()
    return _out(saved)


@router.get("/automations/rules/preview")
def preview_rule(condition: str = Query(...), days: int = Query(..., ge=0, le=60),
                 status: str | None = Query(None), db: Session = Depends(get_db),
                 user: User = editors) -> dict:
    """Ile otwartych kontenerów spełnia warunek dziś — tylko w zakresie użytkownika."""
    try:
        rule = rules_engine.Rule.model_validate(
            {"name": "podgląd", "condition": condition, "days": days, "status": status})
    except ValidationError as exc:
        raise HTTPException(422, "Nieprawidłowy warunek reguły") from exc
    where = rules_engine.clause(rule, today_pl(), utcnow())
    count = db.scalar(scope_containers(select(func.count(Container.id)).where(where), user)) or 0
    sample = db.execute(scope_containers(
        select(Container.id, Container.container_no).where(where), user)
        .order_by(Container.notify_date, Container.id).limit(PREVIEW_SAMPLE)).all()
    return {"count": count, "sample": [{"id": i, "container_no": no} for i, no in sample]}
