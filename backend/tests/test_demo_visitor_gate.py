"""Bramka „przedstaw się” przed kontem demo: formularz, honeypot, retencja 90 dni, lista admina."""
import datetime

import pytest
from sqlalchemy import select

from app.config import settings
from app.models import DemoVisitor, Role, User, utcnow
from app.security import hash_password

GOOD = {"first_name": "Jan", "last_name": "Kowalski", "company": "ACME Sp. z o.o.", "consent": True}


@pytest.fixture
def gate(db_session, monkeypatch):
    monkeypatch.setattr(settings, "demo_readonly_logins", "demo")
    monkeypatch.setattr(settings, "demo_visitor_gate", True)
    db_session.add(User(login="demo", full_name="Demo", role=Role.warehouse,
                        hashed_password=hash_password("demopass1"), is_active=True))
    db_session.commit()


def _login(client):
    return client.post("/api/auth/login", data={"username": "demo", "password": "demopass1"})


def test_demo_login_without_registration_is_refused(client, gate):
    r = _login(client)
    assert r.status_code == 428
    assert "przedstaw się" in r.json()["detail"]


def test_registration_creates_record_and_opens_demo(client, gate, db_session):
    r = client.post("/api/public/demo-visitor", json=GOOD)
    assert r.status_code == 204
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie and "max-age=2592000" in cookie
    row = db_session.scalars(select(DemoVisitor)).one()
    assert (row.first_name, row.last_name, row.company) == ("Jan", "Kowalski", "ACME Sp. z o.o.")
    assert _login(client).status_code == 200


@pytest.mark.parametrize("patch", [
    {"first_name": ""}, {"last_name": "K"}, {"company": " " * 5}, {"company": "x" * 101},
    {"first_name": "Ja\x00n"}, {"consent": False},
])
def test_invalid_form_is_refused(client, gate, db_session, patch):
    r = client.post("/api/public/demo-visitor", json={**GOOD, **patch})
    assert r.status_code == 422
    assert db_session.scalars(select(DemoVisitor)).first() is None
    assert _login(client).status_code == 428


def test_honeypot_is_refused(client, gate, db_session):
    r = client.post("/api/public/demo-visitor", json={**GOOD, "website": "http://spam"})
    assert r.status_code == 400
    assert db_session.scalars(select(DemoVisitor)).first() is None
    assert _login(client).status_code == 428


def test_forged_cookie_does_not_open_demo(client, gate):
    client.cookies.set("demo_visitor", "nie-token")
    assert _login(client).status_code == 428


def test_gate_off_or_regular_login_unaffected(client, gate, db_session, monkeypatch):
    db_session.add(User(login="zwykly", full_name="Z", role=Role.warehouse,
                        hashed_password=hash_password("zwykly123"), is_active=True))
    db_session.commit()
    ok = client.post("/api/auth/login", data={"username": "zwykly", "password": "zwykly123"})
    assert ok.status_code == 200
    client.cookies.clear()
    monkeypatch.setattr(settings, "demo_visitor_gate", False)
    assert _login(client).status_code == 200


def test_health_not_gated(client, gate):
    assert client.get("/api/health").status_code == 200


def test_retention_90_days_on_write(client, gate, db_session):
    old = utcnow() - datetime.timedelta(days=91)
    fresh = utcnow() - datetime.timedelta(days=89)
    db_session.add_all([DemoVisitor(first_name="Stary", last_name="Wpis", company="X1", created_at=old),
                        DemoVisitor(first_name="Świeży", last_name="Wpis", company="X2", created_at=fresh)])
    db_session.commit()
    assert client.post("/api/public/demo-visitor", json=GOOD).status_code == 204
    names = {v.first_name for v in db_session.scalars(select(DemoVisitor))}
    assert names == {"Świeży", "Jan"}


def test_admin_list_newest_first_and_admin_only(client, gate, db_session, admin_headers):
    t = utcnow()
    db_session.add_all([
        DemoVisitor(first_name="A", last_name="Pierwszy", company="=cmd", created_at=t - datetime.timedelta(days=2)),
        DemoVisitor(first_name="B", last_name="Drugi", company="Firma", created_at=t)])
    db_session.commit()
    rows = client.get("/api/admin/demo-visitors", headers=admin_headers).json()
    assert [r["first_name"] for r in rows] == ["B", "A"]
    csv_body = client.get("/api/admin/demo-visitors.csv", headers=admin_headers).text
    assert "'=cmd" in csv_body and ",=cmd" not in csv_body
    client.cookies.clear()
    assert client.get("/api/admin/demo-visitors").status_code == 401
    assert client.post("/api/public/demo-visitor", json=GOOD).status_code == 204
    viewer = {"Authorization": f"Bearer {_login(client).json()['access_token']}"}
    assert client.get("/api/admin/demo-visitors", headers=viewer).status_code == 403
    assert client.get("/api/admin/demo-visitors.csv", headers=viewer).status_code == 403
