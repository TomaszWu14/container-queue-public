"""Pulpit analityczny (widok w stylu Power BI, prośba PO): przepływ kontenerów przez etapy procesu,
podział wg transportu, portu i stanu odprawy oraz rozładunki tydzień po tygodniu.

Same zliczenia w zakresie użytkownika (izolacja: scope_containers) — jedno zapytanie na wykres,
bez hydratacji kontenerów. Stan odprawy jest pusty (None) dla ról, które nie widzą odprawy."""
import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import NonWarehouseViewers as non_warehouse
from ..deps import scope_containers
from ..models import (CUSTOMS_CLEARED, CUSTOMS_IN_PROGRESS, Container, ContainerStatus, Port,
                      TransportType, User, today_pl)
from .containers_common import hidden_fields

# sub-router bez prefiksu — podpinany w routers/containers.py (prefiks /api)
router = APIRouter()

TOP_PORTS = 4          # więcej wycinków w kole jest nieczytelne — reszta idzie do „Inne”
WEEKS_BACK, WEEKS_AHEAD = 5, 4
_MODES = (TransportType.morski, TransportType.kolej, TransportType.lotniczy)


def _week_start(day: datetime.date) -> datetime.date:
    return day - datetime.timedelta(days=day.weekday())


@router.get("/stats/overview")
def overview(today: datetime.date | None = Query(None), db: Session = Depends(get_db),
             user: User = non_warehouse) -> dict:
    utc_today = today_pl()
    if today is None or abs((today - utc_today).days) > 1:
        today = utc_today

    def open_q(*cols):
        return scope_containers(select(*cols).where(Container.open_in_queue()), user)

    by_status = dict(db.execute(open_q(Container.status, func.count()).group_by(Container.status)).all())
    stages = [{"status": s.value, "count": by_status.get(s, 0)}
              for s in ContainerStatus if s != ContainerStatus.ZREALIZOWANY]

    by_mode = dict(db.execute(open_q(Container.transport_type, func.count())
                              .group_by(Container.transport_type)).all())
    transport = [{"key": m.value, "count": by_mode.get(m, 0)} for m in _MODES]
    transport.append({"key": "inne", "count": sum(n for m, n in by_mode.items() if m not in _MODES)})

    ports_rows = db.execute(scope_containers(
        select(Port.name, func.count()).select_from(Container)
        .outerjoin(Port, Port.id == Container.port_id).where(Container.open_in_queue())
        .group_by(Port.name).order_by(func.count().desc(), Port.name), user)).all()
    named = [(name, n) for name, n in ports_rows if name]
    ports = [{"name": name, "count": n} for name, n in named[:TOP_PORTS]]
    other = sum(n for _, n in named[TOP_PORTS:]) + sum(n for name, n in ports_rows if not name)
    if other:
        ports.append({"name": None, "count": other})

    customs = None
    if "customs_status" not in hidden_fields(user):
        in_progress, cleared, total = db.execute(open_q(
            func.count().filter(Container.customs_status.in_(CUSTOMS_IN_PROGRESS)),
            func.count().filter(Container.customs_status.in_(CUSTOMS_CLEARED)),
            func.count())).one()
        customs = {"not_started": total - in_progress - cleared, "in_progress": in_progress,
                   "cleared": cleared}

    first = _week_start(today) - datetime.timedelta(weeks=WEEKS_BACK)
    last = _week_start(today) + datetime.timedelta(weeks=WEEKS_AHEAD + 1)
    days = db.execute(scope_containers(
        select(Container.notify_date, func.count())
        .where(Container.notify_date >= first, Container.notify_date < last)
        .group_by(Container.notify_date), user)).all()
    per_week: dict[datetime.date, int] = {}
    for day, n in days:
        per_week[_week_start(day)] = per_week.get(_week_start(day), 0) + n
    weeks = [{"week": (first + datetime.timedelta(weeks=k)).isoformat(),
              "count": per_week.get(first + datetime.timedelta(weeks=k), 0),
              "current": first + datetime.timedelta(weeks=k) == _week_start(today)}
             for k in range(WEEKS_BACK + WEEKS_AHEAD + 1)]

    return {"stages": stages, "transport": transport, "ports": ports, "customs": customs,
            "weeks": weeks}
