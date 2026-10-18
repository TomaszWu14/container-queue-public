"""US-037: jakość odczytu faktur — źródło dopasowania pozycji (reguły / ML / człowiek / otwarte)
tydzień po tygodniu i trafność podpowiedzi modelu w przedziałach pewności; zakres spółek."""
import datetime as dt

from app.database import SessionLocal
from app.models import (Company, Container, InvoiceBatch, InvoiceItem, InvoiceJob, InvoiceMatchStatus,
                        Role, User, utcnow)
from app.security import hash_password

from .conftest import login

M, U = InvoiceMatchStatus.matched, InvoiceMatchStatus.unmatched


def _items(company_id, no, items, days_ago=0):
    with SessionLocal() as db:
        c = Container(container_no=no, company_id=company_id)
        db.add(c)
        db.flush()
        batch = InvoiceBatch(container_id=c.id)
        db.add(batch)
        db.flush()
        job = InvoiceJob(batch_id=batch.id, filename="f.pdf", stored_name="x.pdf",
                         created_at=utcnow() - dt.timedelta(days=days_ago))
        db.add(job)
        db.flush()
        for i, (status, source, master, sugg, conf) in enumerate(items, start=1):
            db.add(InvoiceItem(job_id=job.id, line_no=i, match_status=status, match_source=source,
                               master_ref=master, ml_suggestion=sugg, ml_confidence=conf))
        db.commit()


def _companies():
    with SessionLocal() as db:
        return [c.id for c in db.query(Company).order_by(Company.id).limit(2)]


def test_sources_per_week_and_calibration(client, admin_headers):
    a, _ = _companies()
    _items(a, "AIQU1000001", [
        (M, "rules", "R1", "", None),
        (M, "ml", "R2", "R2", 0.95),          # automat ML, trafiony
        (M, "user", "R3", "R9", 0.93),        # automat ML poprawiony przez operatora → pudło w „auto”
        (M, "user", "R4", "R4", 0.8),         # podpowiedź „wysoka”, operator potwierdził
        (M, "user", "R5", "R7", 0.5),         # podpowiedź „niska”, inna decyzja
        (U, "", "", "R6", 0.6),               # podpowiedź bez decyzji — nie liczy się do trafności
    ])
    _items(a, "AIQU1000002", [(M, "rules", "R1", "", None)], days_ago=7)
    body = client.get("/api/automations/ai-quality", headers=admin_headers).json()
    assert len(body["weeks"]) == 8
    this, last = body["weeks"][-1], body["weeks"][-2]
    assert (this["rules"], this["ml"], this["user"], this["open"]) == (1, 1, 3, 1)
    assert last["rules"] >= 1
    assert body["totals"]["items"] >= 7
    b = {x["bucket"]: x for x in body["buckets"]}
    assert (b["auto"]["decided"], b["auto"]["hits"], b["auto"]["hit_pct"]) == (2, 1, 50)
    assert (b["high"]["hits"], b["low"]["hits"], b["low"]["suggested"]) == (1, 0, 2)
    assert body["threshold"] == 0.9 and body["ml_hit_pct"] == 50


def test_scoped_to_user_companies(client, admin_headers):
    a, b = _companies()
    _items(a, "AIQU2000001", [(M, "rules", "R1", "", None)])
    _items(b, "AIQU2000002", [(M, "user", "R1", "R1", 0.8), (M, "user", "R2", "R2", 0.8)])
    with SessionLocal() as db:
        db.add(User(login="logi-aiq", hashed_password=hash_password("pass12345"), role=Role.logistics,
                    company_id=a))
        db.commit()
    mine = client.get("/api/automations/ai-quality", headers=login(client, "logi-aiq", "pass12345")).json()
    everyone = client.get("/api/automations/ai-quality", headers=admin_headers).json()
    assert mine["totals"]["user"] == 0 and mine["ml_hit_pct"] is None
    assert everyone["totals"]["user"] == 2 and everyone["ml_hit_pct"] == 100
    assert client.get("/api/automations/ai-quality?weeks=99", headers=admin_headers).status_code == 422


def test_empty_is_not_an_error(client, admin_headers):
    body = client.get("/api/automations/ai-quality?weeks=4", headers=admin_headers).json()
    assert len(body["weeks"]) == 4 and body["automated_pct"] in (None, *range(101))


def test_mistakes_list_corrections_scoped_and_ordered(client, admin_headers):
    """Druga lista PO, pkt 8: poprawki człowieka wobec podpowiedzi modelu — najpierw te, które automat
    ustawiłby sam (≥ progu); trafienia, pozycje bez decyzji i cudza spółka poza listą."""
    a, b = _companies()
    _items(a, "AIQU3000001", [
        (M, "user", "R1", "R9", 0.6),      # pomyłka, niska pewność
        (M, "user", "R2", "R8", 0.95),     # pomyłka, automat by ją ustawił
        (M, "ml", "R3", "R3", 0.97),       # trafienie — nie na liście
        (U, "", "", "R4", 0.9),            # bez decyzji — nie na liście
    ])
    _items(b, "AIQU3000002", [(M, "user", "R5", "R7", 0.99)])
    with SessionLocal() as db:
        db.add(User(login="logi-mis", hashed_password=hash_password("pass12345"), role=Role.logistics,
                    company_id=a))
        db.commit()
    mine = client.get("/api/automations/ai-quality/mistakes", headers=login(client, "logi-mis", "pass12345")).json()
    ours = [m for m in mine if m["container_no"] == "AIQU3000001"]
    assert [(m["suggestion"], m["chosen"], m["auto"]) for m in ours] == [("R8", "R2", True), ("R9", "R1", False)]
    assert not any(m["container_no"] == "AIQU3000002" for m in mine)
    assert client.get("/api/automations/ai-quality/mistakes?limit=99", headers=admin_headers).status_code == 422
