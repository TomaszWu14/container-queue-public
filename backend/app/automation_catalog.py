"""Katalog automatyzacji (US-032, pomysł 1 PO) i pilnowanie automatów (US-033, pomysł 17).

Jedna lista tego, co aplikacja robi sama: pętle tła z `jobs.build_jobs` (harmonogram) i obiegi
wyzwalane z zewnątrz przez n8n (poczta → poczekalnia, draft SAD z poczty) oraz zdarzenia,
które aplikacja wysyła do n8n. Nazwy i opisy żyją w tłumaczeniach ekranu
(`frontend/src/i18n/features/automatyzacje.ts`, klucz = `key`) — tu są tylko powiązania z kodem.

Status automatu z harmonogramu (pilnowanie, jak głęboki health check OBS-009):
- `off` — automat wyłączony w konfiguracji (pętla nie powstaje),
- `error` — ostatni przebieg skończył się błędem,
- `late` — brak udanego przebiegu w oknie interwał + zapas (`JOB_GRACE_S`),
- `ok` — ostatni przebieg udany i na czas; `unknown` — brak przebiegów w dzienniku (30 dni).
"""
from __future__ import annotations

import datetime
from typing import NamedTuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import jobs
from .config import settings
from .models import JobRun, utcnow

JOB_GRACE_S = 3600          # jak routers/health.py: 6 h → alarm po 7 h
WINDOW_DAYS = 7             # okno liczników na ekranie


class Scheduled(NamedTuple):
    key: str                # klucz tłumaczeń: auto_<key>_name / _trigger / _action
    category: str           # alerts | documents | communication | data | integrations
    job: str                # nazwa pętli w jobs.build_jobs
    fns: tuple[str, ...]    # funkcje pętli, które składają się na ten automat


class Event(NamedTuple):
    key: str
    category: str
    source: str             # skąd liczymy przebiegi: intake_mail | sad_mail | outbound


SCHEDULED: tuple[Scheduled, ...] = (
    Scheduled("demurrage", "alerts", "demurrage", ("check_demurrage_alerts",)),
    Scheduled("customs_delay", "alerts", "customs_delay", ("check_customs_alerts",)),
    Scheduled("missing_docs", "alerts", "customs_delay", ("check_docs_alerts",)),
    Scheduled("forecast", "alerts", "customs_delay", ("check_forecast_alerts",)),
    Scheduled("tracking", "alerts", "customs_delay", ("check_tracking_alerts",)),
    Scheduled("stale_import", "alerts", "customs_delay", ("check_stale_import_alerts",)),
    Scheduled("pallet_urgent", "alerts", "pallet_urgent", ("check_pallet_urgent_alerts",)),
    Scheduled("custom_rules", "alerts", "automation_rules", ("run_rules",)),
    Scheduled("invoice_ingest", "documents", "invoice_ingest", ("process_pending",)),
    Scheduled("complaint_drafts", "documents", "complaints", ("check_complaint_auto_drafts",)),
    Scheduled("complaint_reminders", "communication", "complaints", ("check_complaint_reminders",)),
    Scheduled("sms_reminders", "communication", "sms_reminders", ("send_tomorrow_sms",)),
    Scheduled("daily_digest", "communication", "daily_digest", ("check_daily_digest_alerts",)),
    Scheduled("weekly_digest", "communication", "weekly_digest", ("check_weekly_digest_alerts",)),
    Scheduled("automation_report", "communication", "weekly_digest", ("check_automation_weekly_report",)),
    Scheduled("avizo_maintenance", "data", "avizo_maintenance", ("run_maintenance",)),
    Scheduled("driver_data_purge", "data", "avizo_maintenance", ("purge_driver_id_no",)),
    Scheduled("retention", "data", "applog_retention",
              ("purge", "purge_auth_audit", "purge_expired_tokens", "purge_sms_messages",
               "purge_client_errors", "purge_login_failures", "purge_read_notifications")),
    Scheduled("orphan_files", "data", "orphan_files", ("quarantine_orphans",)),
    Scheduled("verify_backup", "data", "verify_backup", ("verify_backup_weekly",)),
    Scheduled("watchdog", "data", "automation_watchdog", ("check_late_automations",)),
    Scheduled("sharepoint_sync", "integrations", "sharepoint_queue", ("sharepoint_queue_sync",)),
    Scheduled("congestion", "integrations", "congestion",
              ("record_port_congestion", "check_congestion_alerts")),
)

EVENTS: tuple[Event, ...] = (
    Event("mail_intake", "integrations", "intake_mail"),
    Event("sad_from_mail", "integrations", "sad_mail"),
    Event("outbound_events", "integrations", "outbound"),
)


def _intervals() -> dict[str, float]:
    """Interwały pętli włączonych w tej konfiguracji (ta sama funkcja, co start aplikacji)."""
    with_ais = bool(settings.aisstream_api_key.strip())
    return {job.name: job.interval_s for job in jobs.build_jobs(with_ais=with_ais)}


def _int_detail(detail: str) -> int:
    """Funkcje alertów zwracają liczbę utworzonych powiadomień — zapisaną jako repr w `detail`."""
    return int(detail) if detail.isdigit() else 0


def _status(*, enabled: bool, last_run: JobRun | None, last_ok_at: datetime.datetime | None,
            interval_s: float | None, now: datetime.datetime) -> str:
    if not enabled:
        return "off"
    if last_run is None:
        return "unknown"
    if not last_run.ok:
        return "error"
    if interval_s is not None and last_ok_at is not None \
            and (now - last_ok_at).total_seconds() > interval_s + JOB_GRACE_S:
        return "late"
    return "ok"


def _scheduled_rows(db: Session, now: datetime.datetime) -> list[dict]:
    intervals = _intervals()
    since = now - datetime.timedelta(days=WINDOW_DAYS)
    pairs = {(s.job, fn) for s in SCHEDULED for fn in s.fns}
    jobs_used = {job for job, _ in pairs}
    runs = db.execute(select(JobRun.job, JobRun.fn, JobRun.ok, JobRun.detail)
                      .where(JobRun.job.in_(jobs_used), JobRun.started_at >= since)).all()
    per_pair: dict[tuple[str, str], list[int]] = {}   # [przebiegi, błędy, efekty]
    for job, fn, ok, detail in runs:
        counts = per_pair.setdefault((job, fn), [0, 0, 0])
        counts[0] += 1
        counts[1] += 0 if ok else 1
        counts[2] += _int_detail(detail or "") if ok else 0
    latest_at = dict(((job, fn), at) for job, fn, at in db.execute(
        select(JobRun.job, JobRun.fn, func.max(JobRun.started_at))
        .where(JobRun.job.in_(jobs_used)).group_by(JobRun.job, JobRun.fn)).all())
    last_ok = dict(((job, fn), at) for job, fn, at in db.execute(
        select(JobRun.job, JobRun.fn, func.max(JobRun.started_at))
        .where(JobRun.job.in_(jobs_used), JobRun.ok.is_(True))
        .group_by(JobRun.job, JobRun.fn)).all())
    latest_runs = {(r.job, r.fn): r for r in db.scalars(select(JobRun).where(
        JobRun.job.in_(jobs_used), JobRun.started_at.in_(list(latest_at.values()) or [now])))
        if latest_at.get((r.job, r.fn)) == r.started_at}

    rows = []
    for spec in SCHEDULED:
        enabled = spec.job in intervals
        statuses, last_runs, oks = [], [], []
        runs_n = errors_n = effects_n = 0
        for fn in spec.fns:
            run = latest_runs.get((spec.job, fn))
            ok_at = last_ok.get((spec.job, fn))
            statuses.append(_status(enabled=enabled, last_run=run, last_ok_at=ok_at,
                                    interval_s=intervals.get(spec.job), now=now))
            if run is not None:
                last_runs.append(run.started_at)
            if ok_at is not None:
                oks.append(ok_at)
            fn_runs, fn_errors, fn_effects = per_pair.get((spec.job, fn), [0, 0, 0])
            runs_n, errors_n, effects_n = runs_n + fn_runs, errors_n + fn_errors, effects_n + fn_effects
        rows.append({
            "key": spec.key, "category": spec.category, "kind": "schedule",
            "status": _worst(statuses),
            "interval_s": round(intervals[spec.job]) if enabled else None,
            "last_run_at": max(last_runs).isoformat() if last_runs else None,
            "last_ok_at": max(oks).isoformat() if oks else None,
            "runs": runs_n, "errors": errors_n, "effects": effects_n,
        })
    return rows


_ORDER = ("error", "late", "unknown", "ok", "off")


def _worst(statuses: list[str]) -> str:
    """Automat z kilku funkcji ma status najgorszej z nich (błąd > spóźnienie > brak danych)."""
    return min(statuses, key=_ORDER.index) if statuses else "unknown"


def _event_rows(db: Session, user, now: datetime.datetime) -> list[dict]:
    from .deps import scope_company, scope_containers
    from .models import Container, IntakeBatch, InvoiceBatch, SadDraft
    since = now - datetime.timedelta(days=WINDOW_DAYS)
    rows = []
    for spec in EVENTS:
        count: int | None = 0
        last_at: datetime.datetime | None = None
        enabled = True
        if spec.source == "intake_mail":
            # izolacja: wgrania z poczty tylko spółek użytkownika (jak GET /api/intake/unmatched)
            q = scope_company(select(func.count()).where(IntakeBatch.source == "mail"),
                              IntakeBatch.company_id, user)
            count = db.scalar(q.where(IntakeBatch.created_at >= since))
            last_at = db.scalar(q.with_only_columns(func.max(IntakeBatch.created_at)))
            enabled = bool(settings.automation_api_token)
        elif spec.source == "sad_mail":
            visible = scope_containers(select(Container.id), user)
            q = (select(func.count()).select_from(SadDraft)
                 .join(InvoiceBatch, InvoiceBatch.id == SadDraft.batch_id)
                 .where(SadDraft.source == "automation", InvoiceBatch.container_id.in_(visible)))
            count = db.scalar(q.where(SadDraft.created_at >= since))
            last_at = db.scalar(q.with_only_columns(func.max(SadDraft.created_at)))
            enabled = bool(settings.automation_api_token)
        else:   # zdarzenia wysyłane do n8n (US-035): wynik każdej wysyłki w dzienniku zadań
            rows.append(_outbound_row(db, spec, since))
            continue
        rows.append({
            "key": spec.key, "category": spec.category, "kind": "event",
            "status": ("ok" if count or last_at else "unknown") if enabled else "off",
            "interval_s": None,
            "last_run_at": last_at.isoformat() if last_at else None,
            "last_ok_at": last_at.isoformat() if last_at else None,
            "runs": count, "errors": None, "effects": None,
        })
    return rows


def _outbound_row(db: Session, spec: Event, since: datetime.datetime) -> dict:
    """Zdarzenia do n8n: systemowe (jak pętle tła) — liczone z dziennika zadań, bez treści."""
    from .automation_events import JOB_NAME
    runs, errors = db.execute(
        select(func.count(), func.count().filter(JobRun.ok.is_(False)))
        .where(JobRun.job == JOB_NAME, JobRun.started_at >= since)).one()
    last = db.execute(select(JobRun.started_at, JobRun.ok).where(JobRun.job == JOB_NAME)
                      .order_by(JobRun.started_at.desc()).limit(1)).first()
    last_ok = db.scalar(select(func.max(JobRun.started_at))
                        .where(JobRun.job == JOB_NAME, JobRun.ok.is_(True)))
    if not settings.automation_webhook_url:
        status = "off"
    elif last is None:
        status = "unknown"
    else:
        status = "ok" if last.ok else "error"
    return {"key": spec.key, "category": spec.category, "kind": "event", "status": status,
            "interval_s": None, "last_run_at": last.started_at.isoformat() if last else None,
            "last_ok_at": last_ok.isoformat() if last_ok else None,
            "runs": runs, "errors": errors, "effects": None}


def catalog(db: Session, user, now: datetime.datetime | None = None) -> dict:
    now = now or utcnow()
    from . import automation_savings
    items = _scheduled_rows(db, now) + _event_rows(db, user, now)
    savings = automation_savings.apply(items, automation_savings.minutes(db))   # US-034
    active = [i for i in items if i["status"] != "off"]
    return {
        "window_days": WINDOW_DAYS,
        "items": items,
        "summary": {
            "total": len(items),
            "active": len(active),
            "attention": sum(1 for i in items if i["status"] in ("error", "late")),
            "runs": sum(i["runs"] or 0 for i in items),
            "effects": sum(i["effects"] or 0 for i in items),
            **savings,
        },
    }
