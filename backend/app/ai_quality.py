"""Jakość odczytu faktur przez automat (US-037, pomysł 14 PO): ile pozycji dopasowały reguły,
ile model ML, ile człowiek — tydzień po tygodniu — i jak trafne są podpowiedzi modelu
w zależności od jego pewności (kalibracja: czy „90% pewności” znaczy ~90% trafień).

Dane są już w bazie: `InvoiceItem.match_source` (rules / ml / user), `ml_suggestion` i
`ml_confidence`. Podpowiedź jest „rozstrzygnięta”, gdy pozycja ma dopasowanie (matched);
trafiona, gdy ostateczny materiał = podpowiedź modelu. Poprawka operatora po automatycznym
dopasowaniu ML zmienia źródło na `user` i liczy się jako pudło — tak model się uczy
(RefModel bierze historię zatwierdzeń operatora).

Zakres danych: paczki faktur kontenerów widocznych dla użytkownika (scope_containers)."""
from __future__ import annotations

import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .models import (Container, InvoiceBatch, InvoiceItem, InvoiceJob, InvoiceMatchStatus, pl_midnight_utc,
                     to_pl_date, utcnow)

SOURCES = ("rules", "ml", "user", "open")


def _bucket(conf: float, threshold: float) -> str:
    if conf >= threshold:
        return "auto"           # ≥ próg: automat sam ustawia dopasowanie
    if conf >= 0.7:
        return "high"
    return "low"


def _week_start(day: datetime.date) -> datetime.date:
    return day - datetime.timedelta(days=day.weekday())


def quality(db: Session, user, weeks: int = 8, now: datetime.datetime | None = None) -> dict:
    from .deps import scope_containers
    now = now or utcnow()
    threshold = float(settings.ml_auto_apply_threshold)
    first_week = _week_start(to_pl_date(now)) - datetime.timedelta(weeks=weeks - 1)
    visible = scope_containers(select(Container.id), user)
    rows = db.execute(
        select(InvoiceJob.created_at, InvoiceItem.match_source, InvoiceItem.match_status,
               InvoiceItem.master_ref, InvoiceItem.ml_suggestion, InvoiceItem.ml_confidence)
        .join(InvoiceJob, InvoiceJob.id == InvoiceItem.job_id)
        .join(InvoiceBatch, InvoiceBatch.id == InvoiceJob.batch_id)
        .where(InvoiceBatch.container_id.in_(visible), InvoiceItem.skipped.is_(False),
               InvoiceJob.created_at >= pl_midnight_utc(first_week))
    ).all()

    week_keys = [first_week + datetime.timedelta(weeks=i) for i in range(weeks)]
    per_week = {w: dict.fromkeys(SOURCES, 0) for w in week_keys}
    buckets = {b: {"suggested": 0, "decided": 0, "hits": 0} for b in ("low", "high", "auto")}
    for created_at, source, status, master_ref, suggestion, conf in rows:
        week = _week_start(to_pl_date(created_at))   # tydzień wg doby polskiej
        done = status == InvoiceMatchStatus.matched
        key = source if done and source in ("rules", "ml", "user") else "open"
        if week in per_week:
            per_week[week][key] += 1
        if suggestion and conf is not None:
            b = buckets[_bucket(float(conf), threshold)]
            b["suggested"] += 1
            if done:
                b["decided"] += 1
                b["hits"] += int(master_ref == suggestion)

    totals = dict.fromkeys(SOURCES, 0)
    for counts in per_week.values():
        for k, v in counts.items():
            totals[k] += v
    items = sum(totals.values())
    decided = sum(b["decided"] for b in buckets.values())
    hits = sum(b["hits"] for b in buckets.values())
    return {
        "weeks": [{"week": w.isoformat(), **per_week[w]} for w in week_keys],
        "totals": {**totals, "items": items},
        "automated_pct": round(100 * (totals["rules"] + totals["ml"]) / items) if items else None,
        "ml_hit_pct": round(100 * hits / decided) if decided else None,
        "threshold": threshold,
        "buckets": [{"bucket": k, **v, "hit_pct": round(100 * v["hits"] / v["decided"]) if v["decided"] else None}
                    for k, v in buckets.items()],
    }
