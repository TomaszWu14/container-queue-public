"""Karta spedytora (czwarta lista PO, pkt 5): jak szybko i jak dobrze spedycje odpowiadają na awizacje.

Z ostatnich WINDOW_DAYS dni, dla każdej spedycji (awizacje w zakresie spółek użytkownika):
- awizacje wysłane i z odpowiedzią,
- mediana czasu odpowiedzi (od wysłania awizacji do pierwszej odpowiedzi spedycji, w godzinach),
- odsetek odpowiedzi w ciągu ON_TIME_HOURS godzin (Z-042),
- odsetek pozycji z prośbą o inny termin i ze zgłoszonym problemem,
- awizacje odrzucone przez logistykę (do poprawy).
Ranking: najpierw odsetek odpowiedzi na czas, potem mediana. Punktualność armatorów (statki) jest osobno —
panel „Punktualność armatorów”. Nic nie zapisujemy."""
from __future__ import annotations

import datetime
from collections import defaultdict
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import AvizoRequest, DeliveryConfirmation, Forwarder, utcnow
from .process_mining import _percentile

WINDOW_DAYS = 90
ON_TIME_HOURS = 24


def _pct(part: int, whole: int) -> float | None:
    return round(100 * part / whole, 1) if whole else None


def scorecard(db: Session, user, now: datetime.datetime | None = None) -> dict:
    from .deps import scope_company
    now = now or utcnow()
    since = now - datetime.timedelta(days=WINDOW_DAYS)
    requests = db.execute(scope_company(
        select(AvizoRequest.id, AvizoRequest.forwarder_id, AvizoRequest.created_at, AvizoRequest.reject_comment)
        .where(AvizoRequest.created_at >= since), AvizoRequest.company_id, user)).all()
    ids = [r.id for r in requests]
    first_answer: dict[int, datetime.datetime] = {}
    decisions: dict[int, list[str]] = defaultdict(list)
    if ids:
        first_answer = dict(db.execute(
            select(DeliveryConfirmation.request_id, func.min(DeliveryConfirmation.submitted_at))
            .where(DeliveryConfirmation.request_id.in_(ids)).group_by(DeliveryConfirmation.request_id)).all())
        for rid, decision in db.execute(select(DeliveryConfirmation.request_id, DeliveryConfirmation.decision)
                                        .where(DeliveryConfirmation.request_id.in_(ids))):
            decisions[rid].append(decision)
    by_fwd: dict[int, list] = defaultdict(list)
    for r in requests:
        by_fwd[r.forwarder_id].append(r)
    names = dict(db.execute(select(Forwarder.id, Forwarder.name).where(Forwarder.id.in_(list(by_fwd)))).all())
    rows: list[dict[str, Any]] = []
    for fid, reqs in by_fwd.items():
        hours = [(first_answer[r.id] - r.created_at).total_seconds() / 3600 for r in reqs if r.id in first_answer]
        items = [d for r in reqs for d in decisions.get(r.id, [])]
        rows.append({
            "forwarder": names.get(fid, "?"), "requests": len(reqs), "answered": len(hours),
            "median_hours": round(_percentile(hours, 0.5), 1) if hours else None,
            "on_time_pct": _pct(sum(h <= ON_TIME_HOURS for h in hours), len(reqs)),
            "date_change_pct": _pct(items.count("date_change"), len(items)),
            "problem_pct": _pct(items.count("problem"), len(items)),
            "rejected": sum(1 for r in reqs if (r.reject_comment or "").strip()),
        })
    rows.sort(key=lambda x: (-(x["on_time_pct"] or 0), x["median_hours"] if x["median_hours"] is not None else 1e9,
                             x["forwarder"]))
    return {"window_days": WINDOW_DAYS, "on_time_hours": ON_TIME_HOURS, "forwarders": rows}
