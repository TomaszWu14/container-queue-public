"""Ograniczenia widoków kont demo (app/demo_limits.py): odczyty ze skutkiem ubocznym, dziennik
zmian, eksporty, MAG-1 i powiadomienia są dla demo wyłączone; obecność i pogoda bez efektu."""
import pytest

from app.config import settings
from app.models import Container, DocumentStatus, Role, User
from app.security import hash_password
from tests.conftest import login
from tests.test_invoice_agency_mail import _assign_agency, _ready_batch
from tests.test_invoices_api import fake_pdf  # noqa: F401

PW = "Demo-Portfolio-2026"


@pytest.fixture
def demo(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "demo_readonly_logins", "demo")
    db_session.add(User(login="demo", hashed_password=hash_password(PW), role=Role.logistics,
                        view_all_companies=True))
    db_session.commit()
    return login(client, "demo", PW)


def test_demo_mail_download_does_not_mark_documents_sent(client, admin_headers, fake_pdf,  # noqa: F811
                                                         db_session, demo):
    cid, bid = _ready_batch(client, admin_headers)
    _assign_agency(db_session, cid)
    before = db_session.get(Container, cid).document_status
    assert before != DocumentStatus.WYSLANE

    for path in (f"/api/invoice-batches/{bid}/agency-mail.eml", f"/api/invoice-batches/{bid}/sadue.xml"):
        resp = client.get(path, headers=demo)
        assert resp.status_code == 403 and "demo" in resp.json()["detail"]
    db_session.expire_all()
    assert db_session.get(Container, cid).document_status == before
    # podgląd (bez skutków) nadal działa — gość widzi, co poszłoby do agencji
    assert client.get(f"/api/invoice-batches/{bid}/agency-mail/preview", headers=demo).status_code == 200
    # zwykłe konto: bez zmian
    assert client.get(f"/api/invoice-batches/{bid}/agency-mail.eml", headers=admin_headers).status_code == 200


@pytest.mark.parametrize("path", [
    "/api/changes/feed", "/api/audit", "/api/containers/1/attachments/zip",
    "/api/archive/attachments-zip?company_code=X&month=2026-10", "/api/containers/export/xlsx",
    "/api/import/sap-imports/1/errors.xlsx", "/api/stats/transport-jobs.csv",
    "/api/pallet-calls", "/api/stock-targets", "/api/notifications",
    "/api/notifications/unread-count",
])
def test_demo_blocked_views(client, demo, path):
    resp = client.get(path, headers=demo)
    assert resp.status_code == 403 and "demo" in resp.json()["detail"]


def test_demo_keeps_main_views(client, demo):
    for path in ("/api/containers", "/api/auth/me", "/api/tracking/map"):
        assert client.get(path, headers=demo).status_code == 200, path


def test_other_accounts_not_limited(client, admin_headers, demo):
    assert client.get("/api/changes/feed", headers=admin_headers).status_code == 200
    assert client.get("/api/notifications/unread-count", headers=admin_headers).status_code == 200


def test_demo_presence_invisible_both_ways(client, admin_headers, demo):
    assert client.post("/api/presence", headers=demo, json={"path": "/kolejka", "active": True}).json() == []
    others = client.post("/api/presence", headers=admin_headers, json={"path": "/kolejka", "active": True}).json()
    assert all(row.get("name") != "demo" for row in others)


def test_demo_weather_skips_external_service(client, demo, monkeypatch):
    from app.tracking import weather

    def boom(db):
        raise AssertionError("demo nie może odpytywać open-meteo")
    monkeypatch.setattr(weather, "fetch_weather", boom)
    assert client.get("/api/tracking/weather", headers=demo).json() == []
