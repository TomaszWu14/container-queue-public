"""„Symuluj dzień” (US-040, pomysł 6 PO): jeden przycisk przechodzi obieg automatów na danych demo.

Bez zapisu do bazy: konto demo tylko czyta (security._enforce_demo_readonly) i tak zostaje. Każdy
krok woła PRAWDZIWĄ funkcję aplikacji na danych widocznych dla użytkownika i pokazuje jej wynik:

1. mail od spedytora → odczyt numeru kontenera z treści (`found_container_numbers`, cyfra kontrolna ISO 6346),
2. faktura tego kontenera → kto dopasował pozycje (reguły / model ML / człowiek / do decyzji),
3. reguły z kreatora → ile kontenerów spełnia każdą dziś (`automation_rules.matching`, zakres użytkownika),
4. zdarzenie do n8n → koperta zdarzenia i podpis HMAC (`automation_events.envelope` / `sign_payload`),
5. podsumowanie → minuty pracy ręcznej wg założeń licznika oszczędności (Z-024).

Nic nie jest wysyłane ani zapisywane — wynik to opis tego, co automaty zrobiłyby z tymi danymi."""
from __future__ import annotations

import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import automation_events, automation_rules, automation_savings
from .invoices.suggestions import found_container_numbers
from .models import Container, InvoiceBatch, InvoiceItem, InvoiceJob, InvoiceMatchStatus, User
from .models.enums import ContainerStatus as S

PREFERRED = (S.W_PORCIE, S.ODPRAWA, S.W_TRANSPORCIE, S.AWIZOWANY)
DEMO_SECRET = "demo-symulacja"     # tylko do pokazania podpisu; prawdziwy sekret nie opuszcza serwera


def _pick(db: Session, user: User) -> Container | None:
    from .deps import scope_containers
    with_invoice = select(InvoiceBatch.container_id)
    for only_invoiced in (True, False):
        q = select(Container).where(Container.status.in_(PREFERRED), Container.container_no != "")
        if only_invoiced:
            q = q.where(Container.id.in_(with_invoice))
        found = db.scalars(scope_containers(q, user).order_by(Container.eta.desc(), Container.id).limit(1)).first()
        if found:
            return found
    return None


def _invoice(db: Session, container: Container) -> dict | None:
    job = db.scalars(select(InvoiceJob).join(InvoiceBatch, InvoiceBatch.id == InvoiceJob.batch_id)
                     .where(InvoiceBatch.container_id == container.id)
                     .order_by(InvoiceJob.created_at.desc()).limit(1)).first()
    if job is None:
        return None
    counts = dict.fromkeys(("rules", "ml", "user", "open"), 0)
    for source, status_, n in db.execute(
            select(InvoiceItem.match_source, InvoiceItem.match_status, func.count())
            .where(InvoiceItem.job_id == job.id, InvoiceItem.skipped.is_(False))
            .group_by(InvoiceItem.match_source, InvoiceItem.match_status)):
        key = source if status_ == InvoiceMatchStatus.matched and source in counts else "open"
        counts[key] += n
    return {"invoice_number": job.invoice_number, "lines": sum(counts.values()), **counts}


def simulate(db: Session, user: User) -> dict:
    from .deps import scope_containers
    container = _pick(db, user)
    if container is None:
        return {"available": False}
    minutes = automation_savings.minutes(db)
    mail = (f"Dzień dobry, w załączniku faktura i packing list do kontenera {container.container_no}. "
            "Statek przypłynął, prosimy o zlecenie odprawy. Pozdrawiam, Spedycja Demo")
    found = found_container_numbers(mail)

    invoice = _invoice(db, container)
    enabled = [r for r in automation_rules.load(db) if r.enabled]
    hits = [len(automation_rules.matching(db, r, scope=lambda q: scope_containers(q, user))) for r in enabled]
    rules = [{"name": r.name, "count": n} for r, n in zip(enabled, hits, strict=True)]

    event = automation_events.envelope("container_in_port", f"Kontener {container.container_no} w porcie",
                                       container_no=container.container_no)
    body = json.dumps(event, ensure_ascii=False, separators=(",", ":")).encode()
    signature = automation_events.sign_payload(body, DEMO_SECRET)

    saved = {"mail": minutes["mail_intake"] if found else 0,
             "invoice": minutes["invoice_ingest"] if invoice else 0,
             "rules": minutes["custom_rules"] * sum(hits)}
    return {
        "available": True,
        "container_id": container.id, "container_no": container.container_no,
        "mail": {"text": mail, "found": found},
        "invoice": invoice,
        "rules": rules,
        "event": {"id": event["id"], "event": event["event"], "signature": signature[:23] + "…",
                  "bytes": len(body)},
        "minutes": saved, "total_minutes": sum(saved.values()),
    }
