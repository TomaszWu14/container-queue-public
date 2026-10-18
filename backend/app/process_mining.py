"""Analiza przebiegu procesu z historii zmian (US-038, pomysł 16 PO — „process mining”).

Źródło: dziennik zmian (`audit_log`, encja `containers`, pole `status`). Każda zmiana statusu
kończy pobyt kontenera w poprzednim etapie; pierwszy etap liczony od utworzenia kontenera.
Wynik:
- czas w etapie: liczba przejść, mediana i 90. percentyl (dni) dla pobytów zakończonych w oknie,
- cofnięcia statusu (powroty do wcześniejszego etapu = poprawki w procesie),
- najczęstsze przejścia,
- kontenery „utknięte”: w obiegu (przed dostawą na magazyn), w obecnym etapie dłużej niż 90. percentyl etapu
  (liczone dopiero przy MIN_SAMPLES zakończonych pobytach — mniej to szum).

Zakres danych: kontenery widoczne dla użytkownika (scope_containers)."""
from __future__ import annotations

import datetime
from collections import Counter, defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AuditLog, Container, ContainerStatus, utcnow

FLOW = [s.value for s in ContainerStatus]
TERMINAL = ContainerStatus.ZREALIZOWANY.value
# po dostawie na magazyn towar fizycznie dotarł; oczekiwanie na rozliczenie to nie „utknięcie” w procesie
# dostaw (inaczej lista „do sprawdzenia” zapełnia się dostarczonymi kontenerami) — Z-027
NOT_STUCK = {ContainerStatus.DOSTARCZONY.value, TERMINAL}
MIN_SAMPLES = 5
STUCK_LIMIT = 10
TOP_TRANSITIONS = 8


def _days(delta: datetime.timedelta) -> float:
    return delta.total_seconds() / 86400


def _percentile(values: list[float], q: float) -> float:
    """Percentyl z interpolacją liniową (jak numpy 'linear'); values niepuste."""
    s = sorted(values)
    pos = (len(s) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def analyze(db: Session, user, days: int = 90, now: datetime.datetime | None = None) -> dict:
    from .deps import scope_containers
    now = now or utcnow()
    since = now - datetime.timedelta(days=days)
    scoped = scope_containers(select(Container.id, Container.container_no, Container.status,
                                     Container.created_at), user)
    containers = {cid: (no, status, created) for cid, no, status, created in db.execute(scoped)}
    history: dict[int, list[tuple[datetime.datetime, str | None, str | None]]] = defaultdict(list)
    for cid, at, old, new in db.execute(
            select(AuditLog.entity_id, AuditLog.created_at, AuditLog.old_value, AuditLog.new_value)
            .where(AuditLog.entity_type == "containers", AuditLog.field == "status",
                   AuditLog.entity_id.in_(select(scoped.subquery().c.id)))
            .order_by(AuditLog.entity_id, AuditLog.created_at, AuditLog.id)):
        history[cid].append((at, old, new))

    durations: dict[str, list[float]] = defaultdict(list)
    transitions: Counter[tuple[str, str]] = Counter()
    backward = 0
    entered: dict[int, datetime.datetime] = {}
    for cid, (_no, _status, created) in containers.items():
        start = created
        for at, old, new in history.get(cid, []):
            if at >= since and old in FLOW and new in FLOW:
                durations[old].append(max(0.0, _days(at - start)))
                transitions[(old, new)] += 1
                backward += int(FLOW.index(new) < FLOW.index(old))
            start = at
        entered[cid] = start

    stages = []
    p90: dict[str, float] = {}
    for stage in FLOW:
        if stage == TERMINAL:
            continue
        vals = durations.get(stage, [])
        row: dict = {"status": stage, "count": len(vals), "median_days": None, "p90_days": None}
        if vals:
            row["median_days"] = round(_percentile(vals, 0.5), 1)
            row["p90_days"] = round(_percentile(vals, 0.9), 1)
            if len(vals) >= MIN_SAMPLES:
                p90[stage] = _percentile(vals, 0.9)
        stages.append(row)

    stuck = []
    for cid, (no, status, _created) in containers.items():
        stage = getattr(status, "value", status)
        if stage in p90 and stage not in NOT_STUCK:
            in_stage = _days(now - entered[cid])
            if in_stage > p90[stage]:
                stuck.append({"id": cid, "container_no": no, "status": stage,
                              "days_in_stage": round(in_stage, 1), "p90_days": round(p90[stage], 1)})
    stuck.sort(key=lambda r: r["days_in_stage"] - r["p90_days"], reverse=True)

    total = sum(transitions.values())
    return {
        "days": days,
        "min_samples": MIN_SAMPLES,
        "transitions_total": total,
        "backward": backward,
        "backward_pct": round(100 * backward / total) if total else None,
        "stages": stages,
        "top_transitions": [{"from": a, "to": b, "count": n}
                            for (a, b), n in transitions.most_common(TOP_TRANSITIONS)],
        "stuck_total": len(stuck),
        "stuck": stuck[:STUCK_LIMIT],
    }
