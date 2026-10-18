"""Symulacja „co jeśli statek się spóźni” (druga lista PO, pkt 10) — bez zapisu.

Wybrany statek spóźnia się o N dni: daty awizacji jego kontenerów (w zakresie użytkownika) przesuwają się
o N dni. Liczymy obciążenie magazynów dzień po dniu przed i po przesunięciu tą samą regułą co prognoza
przeciążenia (`notification_digests.check_forecast_alerts`): aktywne kontenery z datą awizacji, bez tranzytów,
limit dzienny magazynu albo nadpisanie na dzień. Wynik: przesunięte kontenery i dni, w których zmienia się
przekroczenie limitu. Nic nie zapisujemy — plan zostaje bez zmian.

Obciążenie dnia to suma wszystkich spółek (limit magazynu jest wspólny), pokazywana wyłącznie jako liczba —
bez danych kontenerów innych spółek."""
from __future__ import annotations

import datetime
from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Container, DailyLimit, Warehouse, today_pl

HORIZON_DAYS = 28
MAX_DELAY = 21


def _open(q):
    return q.where(Container.status.not_in(Container.FINISHED), Container.is_transit.is_(False),
                   Container.warehouse_id.is_not(None), Container.notify_date.is_not(None))


def vessels(db: Session, user) -> list[str]:
    from .deps import scope_containers
    today = today_pl()
    q = _open(select(Container.vessel).where(Container.vessel != "", Container.notify_date >= today))
    return sorted(set(db.scalars(scope_containers(q, user))))


def simulate(db: Session, user, vessel: str, delay: int) -> dict:
    from .deps import scope_containers
    today = today_pl()
    horizon = today + datetime.timedelta(days=HORIZON_DAYS)
    moved = db.execute(scope_containers(_open(
        select(Container.id, Container.container_no, Container.warehouse_id, Container.notify_date)
        .where(Container.vessel == vessel, Container.notify_date >= today)), user)).all()
    shift = datetime.timedelta(days=delay)
    load = Counter({(wid, day): n for wid, day, n in db.execute(_open(
        select(Container.warehouse_id, Container.notify_date, func.count(Container.id))
        .where(Container.notify_date >= today, Container.notify_date <= horizon + shift))
        .group_by(Container.warehouse_id, Container.notify_date)).all()})
    after = Counter(load)
    for _, _, wid, day in moved:
        after[(wid, day)] -= 1
        after[(wid, day + shift)] += 1
    wids = {wid for wid, _ in after}
    names = dict(db.execute(select(Warehouse.id, Warehouse.name).where(Warehouse.id.in_(wids))).all())
    defaults = dict(db.execute(select(Warehouse.id, Warehouse.default_daily_limit)
                               .where(Warehouse.id.in_(wids))).all())
    overrides = {(wid, day): lim for wid, day, lim in db.execute(
        select(DailyLimit.warehouse_id, DailyLimit.day, DailyLimit.limit)
        .where(DailyLimit.warehouse_id.in_(wids), DailyLimit.day >= today)).all()}
    days = []
    for wid, day in sorted(set(load) | set(after), key=lambda k: (k[1], names.get(k[0], ""))):
        limit = overrides.get((wid, day), defaults.get(wid))
        b, a = load.get((wid, day), 0), after.get((wid, day), 0)
        if b == a or limit is None:
            continue
        days.append({"warehouse": names.get(wid, "?"), "day": day.isoformat(), "before": b, "after": a,
                     "limit": limit, "over_before": b > limit, "over_after": a > limit})
    return {
        "vessel": vessel, "delay": delay,
        "containers": [{"id": cid, "container_no": no, "warehouse": names.get(wid, "?"),
                        "from": day.isoformat(), "to": (day + shift).isoformat()}
                       for cid, no, wid, day in sorted(moved, key=lambda r: r[3])],
        "days": days,
        "new_overloads": sum(1 for d in days if d["over_after"] and not d["over_before"]),
        "resolved_overloads": sum(1 for d in days if d["over_before"] and not d["over_after"]),
    }
