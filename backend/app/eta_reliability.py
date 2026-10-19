"""Punktualność armatorów i „realne ETA” (trzecia lista PO, pkt 7).

Z historii: dla kontenerów, które już przypłynęły, liczymy spóźnienie = dzień faktycznego wyładunku
(pierwsze nie-szacowane zdarzenie DISCHARGE/ARRIVE, dzień PL) − pierwsze znane ETA (najstarsza wartość
z dziennika zmian pola `eta`, a bez zmian — bieżące ETA). Grupujemy po armatorze i porcie: liczba przypłynięć,
mediana, 90. percentyl, odsetek spóźnionych o ponad 1 dzień.

„Realne ETA” dla kontenerów w drodze = ETA + mediana spóźnienia jego armatora i portu (bez pary —
sam armator), gdy grupa ma co najmniej `MIN_ARRIVALS` przypłynięć (Z-038). Tylko kontenery w zakresie
użytkownika; nic nie zapisujemy — to podpowiedź, nie zmiana planu."""
from __future__ import annotations

import datetime
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AuditLog, Carrier, Container, ContainerStatus, Port, to_pl_date, today_pl
from .notification_alerts import _arrival_map
from .process_mining import _percentile

WINDOW_DAYS = 365
MIN_ARRIVALS = 3
LATE_DAYS = 1
FORECAST_LIMIT = 20
IN_TRANSIT = (ContainerStatus.TRANSPORT_WSTEPNY, ContainerStatus.W_TRANSPORCIE)


def _first_eta(db: Session, ids: list[int]) -> dict[int, datetime.date]:
    """Najstarsza znana wartość ETA z dziennika zmian (stan sprzed pierwszej zmiany)."""
    out: dict[int, datetime.date] = {}
    if not ids:
        return out
    for cid, old in db.execute(select(AuditLog.entity_id, AuditLog.old_value)
                               .where(AuditLog.entity_type == "containers", AuditLog.field == "eta",
                                      AuditLog.entity_id.in_(ids))
                               .order_by(AuditLog.created_at, AuditLog.id)):
        if cid in out or not old:
            continue
        try:
            out[cid] = datetime.date.fromisoformat(str(old)[:10])
        except ValueError:
            continue
    return out


def _stats(delays: list[float]) -> dict:
    return {"arrivals": len(delays), "median_days": round(_percentile(delays, 0.5), 1),
            "p90_days": round(_percentile(delays, 0.9), 1),
            "late_pct": round(100 * sum(1 for d in delays if d > LATE_DAYS) / len(delays))}


def analyze(db: Session, user, today: datetime.date | None = None) -> dict:
    from .deps import scope_containers
    today = today or today_pl()
    since = today - datetime.timedelta(days=WINDOW_DAYS)
    rows = list(db.scalars(scope_containers(select(Container).where(Container.carrier_id.is_not(None)), user)))
    arrivals = _arrival_map(db, [c.id for c in rows])
    first = _first_eta(db, [c.id for c in rows if c.id in arrivals])
    by_pair: dict[tuple[int, int | None], list[float]] = defaultdict(list)
    by_carrier: dict[int, list[float]] = defaultdict(list)
    for c in rows:
        arrived = arrivals.get(c.id)
        planned = first.get(c.id) or c.eta
        if arrived is None or planned is None or c.carrier_id is None:
            continue
        day = to_pl_date(arrived)
        if day < since:
            continue
        delay = float((day - planned).days)
        by_pair[(c.carrier_id, c.port_id)].append(delay)
        by_carrier[c.carrier_id].append(delay)

    carriers = dict(db.execute(select(Carrier.id, Carrier.name)).all())
    ports = dict(db.execute(select(Port.id, Port.name)).all())
    table = [{"carrier": carriers.get(cid, "?"), "port": ports.get(pid, "—") if pid else "—", **_stats(d)}
             for (cid, pid), d in by_pair.items() if len(d) >= MIN_ARRIVALS]
    table.sort(key=lambda r: (-r["median_days"], r["carrier"], r["port"]))

    forecasts = []
    for c in rows:
        if c.status not in IN_TRANSIT or c.eta is None or c.eta < today or c.id in arrivals or c.carrier_id is None:
            continue
        group = by_pair.get((c.carrier_id, c.port_id), [])
        basis = "carrier_port"
        if len(group) < MIN_ARRIVALS:
            group, basis = by_carrier.get(c.carrier_id, []), "carrier"
        if len(group) < MIN_ARRIVALS:
            continue
        shift = round(_percentile(group, 0.5))
        if shift == 0:
            continue
        forecasts.append({"container_id": c.id, "container_no": c.container_no,
                          "carrier": carriers.get(c.carrier_id, "?"),
                          "port": ports.get(c.port_id, "—") if c.port_id else "—",
                          "eta": c.eta.isoformat(),
                          "realistic_eta": (c.eta + datetime.timedelta(days=shift)).isoformat(),
                          "shift_days": shift, "basis": basis, "arrivals": len(group)})
    forecasts.sort(key=lambda f: (-abs(f["shift_days"]), f["eta"]))
    return {"window_days": WINDOW_DAYS, "min_arrivals": MIN_ARRIVALS, "carriers": table,
            "forecasts": forecasts[:FORECAST_LIMIT], "forecast_total": len(forecasts)}
