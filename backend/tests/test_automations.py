"""US-032/US-033: ekran „Automatyzacje” — katalog automatów aplikacji z licznikami z dziennika
zadań i stanem (pilnowanie: błąd, spóźnienie, wyłączony). Obiegi z poczty w zakresie spółki."""
import datetime as dt

from app import automation_catalog as cat
from app.config import settings
from app.database import SessionLocal
from app.models import Company, IntakeBatch, JobRun, Role, User, utcnow
from app.security import hash_password

from .conftest import login


def _run(job, fn, ago_h, ok=True, detail=""):
    return JobRun(job=job, fn=fn, started_at=utcnow() - dt.timedelta(hours=ago_h),
                  duration_ms=5, ok=ok, detail=detail)


def _user(login_name, role, company_id=None):
    with SessionLocal() as db:
        db.add(User(login=login_name, hashed_password=hash_password("pass12345"), role=role,
                    company_id=company_id))
        db.commit()


def _items(client, headers):
    body = client.get("/api/automations", headers=headers).json()
    return body, {i["key"]: i for i in body["items"]}


def test_catalog_lists_every_scheduled_job_function(client, admin_headers):
    """Każda funkcja pętli tła jest w katalogu (nowy automat bez wpisu = czerwony test),
    poza próbkowaniem monitora, które nie jest automatyzacją procesu."""
    from app.jobs import build_jobs
    listed = {(s.job, fn) for s in cat.SCHEDULED for fn in s.fns}
    built = {(j.name, fn.__name__) for j in build_jobs(with_ais=True) for fn in j.fns
             if j.name != "monitor_sample"}
    assert built - listed == set()
    _, items = _items(client, admin_headers)
    assert {s.key for s in cat.SCHEDULED} | {e.key for e in cat.EVENTS} == set(items)


def test_counts_effects_and_statuses(client, admin_headers):
    with SessionLocal() as db:
        db.add_all([
            _run("demurrage", "check_demurrage_alerts", 1, detail="3"),
            _run("demurrage", "check_demurrage_alerts", 7, detail="2"),
            _run("demurrage", "check_demurrage_alerts", 24 * 10, detail="9"),   # poza oknem 7 dni
            _run("customs_delay", "check_customs_alerts", 1, ok=False, detail="Traceback ..."),
            _run("customs_delay", "check_docs_alerts", 20),   # interwał 6 h + 1 h zapasu → spóźniony
        ])
        db.commit()
    body, items = _items(client, admin_headers)
    demurrage = items["demurrage"]
    assert (demurrage["status"], demurrage["runs"], demurrage["errors"], demurrage["effects"]) \
        == ("ok", 2, 0, 5)
    assert demurrage["interval_s"] == 6 * 3600
    assert items["customs_delay"]["status"] == "error" and items["customs_delay"]["errors"] == 1
    assert items["missing_docs"]["status"] == "late"
    assert items["forecast"]["status"] == "unknown"
    assert body["summary"]["attention"] >= 2
    assert "Traceback" not in str(body)   # treść błędu zostaje w dzienniku admina


def test_disabled_integrations_are_off(client, admin_headers, monkeypatch):
    monkeypatch.setattr(settings, "aisstream_api_key", "")
    monkeypatch.setattr(settings, "automation_webhook_url", "")
    _, items = _items(client, admin_headers)
    assert items["congestion"]["status"] == "off" and items["congestion"]["interval_s"] is None
    assert items["outbound_events"]["status"] == "off"


def test_mail_intake_counted_only_for_own_company(client, admin_headers, monkeypatch):
    monkeypatch.setattr(settings, "automation_api_token", "t" * 40)
    with SessionLocal() as db:
        own, other = db.query(Company).order_by(Company.id).limit(2).all()
        db.add_all([IntakeBatch(company_id=own.id, source="mail"),
                    IntakeBatch(company_id=other.id, source="mail"),
                    IntakeBatch(company_id=own.id, source="manual")])
        db.commit()
        own_id = own.id
    _user("logi-auto", Role.logistics, own_id)
    _, items = _items(client, login(client, "logi-auto", "pass12345"))
    assert items["mail_intake"]["runs"] == 1 and items["mail_intake"]["status"] == "ok"
    _, items = _items(client, admin_headers)
    assert items["mail_intake"]["runs"] == 2


def test_forbidden_for_partners(client, admin_headers):
    _user("mag-auto", Role.warehouse)
    r = client.get("/api/automations", headers=login(client, "mag-auto", "pass12345"))
    assert r.status_code == 403


# --- US-034: licznik oszczędności per automat -------------------------------------------------

def test_default_minutes_cover_whole_catalog():
    from app.automation_savings import DEFAULT_MINUTES
    assert set(DEFAULT_MINUTES) == {s.key for s in cat.SCHEDULED} | {e.key for e in cat.EVENTS}


def test_savings_from_effects_and_mail_runs(client, admin_headers, monkeypatch):
    monkeypatch.setattr(settings, "automation_api_token", "t" * 40)
    with SessionLocal() as db:
        company_id = db.query(Company.id).order_by(Company.id).first()[0]
        db.add_all([_run("demurrage", "check_demurrage_alerts", 1, detail="4"),
                    _run("applog_retention", "purge", 1, detail="900"),   # porządek danych: 0 min
                    IntakeBatch(company_id=company_id, source="mail"),
                    IntakeBatch(company_id=company_id, source="mail")])
        db.commit()
    body, items = _items(client, admin_headers)
    assert items["demurrage"]["minutes_per_effect"] == 5 and items["demurrage"]["minutes_saved"] == 20
    assert items["retention"]["minutes_saved"] == 0
    assert items["mail_intake"]["minutes_saved"] == 10          # 2 maile × 5 min
    assert body["summary"]["minutes_saved"] == 30 and body["summary"]["hours_saved"] == 0.5


def test_admin_changes_minutes_with_audit(client, admin_headers):
    with SessionLocal() as db:
        db.add(_run("demurrage", "check_demurrage_alerts", 1, detail="4"))
        db.commit()
    r = client.put("/api/automations/minutes", headers=admin_headers,
                   json={"minutes": {"demurrage": 12, "tracking": 3}})
    assert r.status_code == 200 and r.json()["minutes"]["demurrage"] == 12
    _, items = _items(client, admin_headers)
    assert items["demurrage"]["minutes_saved"] == 48
    with SessionLocal() as db:
        from app.models import AuditLog
        rows = db.query(AuditLog).filter(AuditLog.field.like("automation_minutes.%")).all()
        assert [(a.field, a.old_value, a.new_value) for a in rows] == [
            ("automation_minutes.demurrage", "5", "12")]   # bez zmiany (tracking 3 → 3) bez wpisu


def test_minutes_validation_and_role(client, admin_headers):
    assert client.put("/api/automations/minutes", headers=admin_headers,
                      json={"minutes": {"nieznany": 5}}).status_code == 422
    assert client.put("/api/automations/minutes", headers=admin_headers,
                      json={"minutes": {"demurrage": 999}}).status_code == 422
    _user("logi-min", Role.logistics)
    r = client.put("/api/automations/minutes", headers=login(client, "logi-min", "pass12345"),
                   json={"minutes": {"demurrage": 1}})
    assert r.status_code == 403
