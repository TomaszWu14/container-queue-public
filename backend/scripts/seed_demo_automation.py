"""Demo: dane dla ekranu „Automatyzacje”, żeby żaden panel nie świecił pustką (top 15 PO, pkt 1).

- dziennik zadań z ostatnich 7 dni: każdy automat z harmonogramu „działał” (co najwyżej raz na godzinę,
  ostatnio przed chwilą), część przebiegów z efektem (np. 2 powiadomienia), jedna dawna awaria śledzenia,
  zdarzenia do n8n — licznik oszczędności i stan automatów mają co pokazać,
- 3 przykładowe reguły z kreatora (US-036), jedna tylko na e-mail i Teams (kanały, US-063),
- paczki faktur z pozycjami z ostatnich 8 tygodni: reguły / model ML / człowiek / do decyzji z pewnością
  modelu — panel „Odczyt faktur” (US-037) pokazuje udział automatu i trafność w przedziałach pewności.

Wszystko zmyślone i deterministyczne (stałe ziarno), jak reszta seed_demo."""
import datetime as dt
import hashlib
import pathlib
import random
import secrets

from app import automation_catalog, automation_events, automation_rules
from app.config import settings
from app.models import (Container, InvoiceBatch, InvoiceDocKind, InvoiceItem, InvoiceJob, InvoiceJobStatus,
                        InvoiceMatchStatus, JobRun)
from app.models.enums import ContainerStatus as S
from scripts.seed_demo_process import _pdf

DAYS = 7
MAX_SPACING_S = 3600          # przebiegi częstszych pętli zapisujemy co godzinę (bez tysięcy wierszy)
INVOICE_WEEKS = 8
INVOICE_CONTAINERS = 24
FLAKY = ("check_tracking_alerts",)   # jedna dawna awaria — widać licznik błędów, stan „działa”
# fn → co ile przebiegów jest efekt (np. powiadomienie); reszta przebiegów kończy się bez efektu
EFFECT_EVERY = {"demurrage": 6, "customs_delay": 8, "missing_docs": 5, "forecast": 1, "tracking": 3,
                "stale_import": 12, "pallet_urgent": 10, "custom_rules": 6, "invoice_ingest": 4,
                "complaint_drafts": 24, "complaint_reminders": 12, "sms_reminders": 6, "daily_digest": 1,
                "weekly_digest": 1, "sharepoint_sync": 8, "congestion": 12, "driver_data_purge": 24}

EXAMPLE_RULES = [
    {"name": "Awizacja za 2 dni, a kontener jeszcze przed odprawą", "condition": "notify_soon_status",
     "days": 2, "status": "ODPRAWA", "notify": "watchers"},
    {"name": "ETA minęło ponad 3 dni temu — sprawdź u armatora", "condition": "eta_passed", "days": 3,
     "notify": "admins", "channels": ["email", "teams"]},
    {"name": "Awizacja jutro, brak kierowcy", "condition": "no_driver", "days": 1, "notify": "watchers"},
]

# (źródło, status, czy podpowiedź trafiona, pewność) — rozkład bliski realnemu po kilku tygodniach nauki
_ITEM_MIX = ([("rules", True, None, None)] * 9 + [("ml", True, True, (0.91, 0.99))] * 12
             + [("user", True, False, (0.90, 0.95))] * 1 + [("user", True, True, (0.70, 0.89))] * 4
             + [("user", True, False, (0.70, 0.89))] * 1 + [("user", True, True, (0.40, 0.69))] * 1
             + [("user", True, False, (0.35, 0.69))] * 2 + [("", False, None, (0.40, 0.85))] * 1)


def job_runs(db, now: dt.datetime) -> int:
    """Przebiegi automatów z harmonogramu i zdarzeń do n8n z ostatnich DAYS dni."""
    rnd = random.Random(2026)
    intervals = automation_catalog._intervals()
    count = 0
    for spec in automation_catalog.SCHEDULED:
        interval = intervals.get(spec.job)
        if interval is None:          # automat wyłączony na tej instancji — stan „wyłączony”
            continue
        spacing = dt.timedelta(seconds=max(interval, MAX_SPACING_S) if interval < 86400 else interval)
        every = EFFECT_EVERY.get(spec.key)
        for fn in spec.fns:
            at, k = now - dt.timedelta(minutes=5 + count % 40), 0
            while at > now - dt.timedelta(days=DAYS):
                failed = fn in FLAKY and dt.timedelta(days=3) <= now - at < dt.timedelta(days=3) + spacing
                effect = rnd.randint(1, 3) if every and k % every == 0 else 0
                db.add(JobRun(job=spec.job, fn=fn, started_at=at, duration_ms=rnd.randint(40, 1800),
                              ok=not failed, detail="HTTP 503 od serwisu śledzenia" if failed else str(effect)))
                at -= spacing
                k += 1
                count += 1
    for k in range(12):               # zdarzenia do n8n (US-035): kontener dostarczony, dzienne podsumowanie
        db.add(JobRun(job=automation_events.JOB_NAME, fn="container_delivered" if k % 3 else "daily_digest",
                      started_at=now - dt.timedelta(hours=7 + 13 * k), duration_ms=rnd.randint(80, 400),
                      ok=True, detail="HTTP 200"))
        count += 1
    return count


def rules(db) -> int:
    saved = automation_rules.save(db, [automation_rules.Rule.model_validate(r) for r in EXAMPLE_RULES])
    return len(saved)


def invoices(db, containers: list[Container], author_id: int, now: dt.datetime) -> int:
    """Paczki faktur z pozycjami (bez OCR — pozycje od razu „przeczytane”), rozłożone na 8 tygodni."""
    rnd = random.Random(14)
    uploads = pathlib.Path(settings.uploads_dir)
    uploads.mkdir(parents=True, exist_ok=True)
    picked = [c for c in containers if c.status not in (S.ZAPOWIEDZIANY, S.W_PRODUKCJI)][:INVOICE_CONTAINERS]
    items = 0
    for i, c in enumerate(picked):
        created = now - dt.timedelta(days=(i * INVOICE_WEEKS * 7) // len(picked), hours=i % 6)
        content = _pdf(f"DEMO CI-{c.container_no} - faktura zmyslona, dane pokazowe")
        name = f"CI_{c.container_no}.pdf"
        stored = f"inv_{c.id}_{secrets.token_hex(8)}_{name}"
        (uploads / stored).write_bytes(content)
        batch = InvoiceBatch(container_id=c.id, ready=True, created_by_id=author_id, created_at=created,
                             updated_at=created)
        db.add(batch)
        db.flush()
        open_lines = i < 3                 # najnowsze paczki: kilka pozycji jeszcze czeka na decyzję
        job = InvoiceJob(batch_id=batch.id, filename=name, stored_name=stored, source_name=name,
                         sha256=hashlib.sha256(content).hexdigest(), doc_kind=InvoiceDocKind.invoice,
                         status=InvoiceJobStatus.extracted if open_lines else InvoiceJobStatus.confirmed,
                         invoice_number=f"CI-2026-{1000 + i}", container_no=c.container_no, created_at=created)
        db.add(job)
        db.flush()
        for line in range(1, 7 + i % 5):
            source, done, hit, conf = rnd.choice(_ITEM_MIX)
            if open_lines and line % 3 == 0:
                source, done, hit, conf = "", False, None, (0.40, 0.85)
            elif not open_lines and not done:
                source, done, hit, conf = "user", True, True, (0.70, 0.89)
            ref = f"DEMO-{(i * 11 + line) % 60:03d}"
            suggestion = "" if conf is None else (ref if hit or not done else f"DEMO-{(i + line * 7) % 60:03d}")
            db.add(InvoiceItem(job_id=job.id, line_no=line, raw_ref=f"SUP-{line:02d}{i:02d}",
                               descr=f"Artykuł demo {line}", qty=str(10 * line), uom_src="PCS",
                               match_status=InvoiceMatchStatus.matched if done else InvoiceMatchStatus.unmatched,
                               match_source=source, master_ref=ref if done else "", ml_suggestion=suggestion,
                               ml_confidence=round(rnd.uniform(*conf), 2) if conf else None))
            items += 1
    return items


def rework(db, containers: list[Container], author_id: int, limit: int = 4) -> int:
    """Kilka cofnięć statusu (odprawa → port → odprawa, np. brak dokumentu u agencji) — analiza przebiegu
    procesu i wykres przepływu pokazują poprawki w procesie, jak w prawdziwych danych."""
    from app.models import AuditLog
    db.flush()
    picked = [c for c in containers if c.status in (S.AWIZOWANY, S.W_DOSTAWIE)][::7][:limit]
    for c in picked:
        rows = (db.query(AuditLog).filter_by(entity_type="containers", entity_id=c.id, field="status")
                .order_by(AuditLog.created_at).all())
        at = next((i for i, r in enumerate(rows) if r.new_value == S.ODPRAWA.value), None)
        if at is None or at + 1 >= len(rows):
            continue
        t1, t2 = rows[at].created_at, rows[at + 1].created_at
        for k, (old, new) in enumerate(((S.ODPRAWA, S.W_PORCIE), (S.W_PORCIE, S.ODPRAWA)), start=1):
            db.add(AuditLog(entity_type="containers", entity_id=c.id, field="status", old_value=old.value,
                            new_value=new.value, user_id=author_id, created_at=t1 + (t2 - t1) * k / 3,
                            note="Agencja: brak świadectwa pochodzenia — powrót do portu, uzupełnione"))
    return len(picked)
