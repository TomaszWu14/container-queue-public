"""„Ile alertów wysłałaby ta reguła?” — test reguły na ostatnich 30 dniach (trzecia lista PO, pkt 2).

Dla każdego dnia z okna sprawdzamy, które kontenery spełniałyby warunek reguły tego dnia (tak jak pętla tła:
jeden alert na kontener i dzień). Przybliżenie, nazwane wprost (Z-037): etap kontenera bierzemy z historii
zmian statusu (stan z tamtego dnia), a daty (ETA, awizacja, wysłanie planu) i dane kierowcy — z dzisiejszych
danych, bo ich wcześniejsze wartości nie zawsze są w historii. Tylko kontenery w zakresie użytkownika;
nic nie jest zapisywane ani wysyłane."""
from __future__ import annotations

import datetime
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import automation_rules as rules_engine
from .models import AuditLog, Container, ContainerStatus, pl_midnight_utc, to_pl_date, today_pl

WINDOW_DAYS = 30
DONE = {s.value for s in rules_engine.DONE}
FLOW = [s.value for s in ContainerStatus]


def _status_on(created: datetime.date, history: list[tuple[datetime.date, str, str]], current: str,
               day: datetime.date) -> str | None:
    """Etap kontenera na koniec dnia `day` z dziennika zmian statusu; None = kontenera jeszcze nie było."""
    if created > day:
        return None
    status = history[0][1] if history and history[0][1] else current
    for when, _old, new in history:
        if when > day:
            break
        status = new
    return status


def _matches(rule: rules_engine.Rule, c: Container, status: str, day: datetime.date) -> bool:
    if status in DONE:
        return False
    horizon = day + datetime.timedelta(days=rule.days)
    if rule.condition == "eta_passed":
        return c.eta is not None and c.eta <= day - datetime.timedelta(days=rule.days)
    if rule.condition == "notify_soon_status":
        before = FLOW[:FLOW.index(rule.status.value)] if rule.status else []
        return c.notify_date is not None and day <= c.notify_date <= horizon and status in before
    if rule.condition == "no_driver":
        return c.notify_date is not None and day <= c.notify_date <= horizon and not (c.driver_name or "").strip()
    sent, confirmed = c.planning_sent_at, c.planning_confirmed_at
    next_day = pl_midnight_utc(day + datetime.timedelta(days=1))     # koniec dnia PL (UTC, wyłącznie)
    return (sent is not None and sent < next_day - datetime.timedelta(days=rule.days)
            and (confirmed is None or confirmed >= next_day))


def backtest(db: Session, rule: rules_engine.Rule, scope, today: datetime.date | None = None,
             days: int = WINDOW_DAYS) -> dict:
    today = today or today_pl()
    start = today - datetime.timedelta(days=days - 1)
    containers = list(db.scalars(scope(select(Container))))
    ids = [c.id for c in containers]
    history: dict[int, list[tuple[datetime.date, str, str]]] = defaultdict(list)
    if ids:
        for cid, at, old, new in db.execute(
                select(AuditLog.entity_id, AuditLog.created_at, AuditLog.old_value, AuditLog.new_value)
                .where(AuditLog.entity_type == "containers", AuditLog.field == "status",
                       AuditLog.entity_id.in_(ids)).order_by(AuditLog.created_at, AuditLog.id)):
            history[cid].append((to_pl_date(at), old or "", new or ""))
    per_day: list[dict] = []
    counts: list[int] = []
    hit: set[int] = set()
    for k in range(days):
        day = start + datetime.timedelta(days=k)
        n = 0
        for c in containers:
            created = to_pl_date(c.created_at) if c.created_at else start
            status = _status_on(created, history[c.id], c.status.value, day)
            if status is not None and _matches(rule, c, status, day):
                n += 1
                hit.add(c.id)
        per_day.append({"day": day.isoformat(), "alerts": n})
        counts.append(n)
    total = sum(counts)
    return {"days": days, "alerts": total, "containers": len(hit),
            "avg_per_day": round(total / days, 1), "max_per_day": max(counts, default=0),
            "per_day": per_day}
