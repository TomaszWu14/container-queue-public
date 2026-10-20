"""Diagnostyka proxy: /api/public/whoami pokazuje IP odwiedzającego tak, jak widzi go aplikacja.
Adres prywatny = aplikacja widzi proxy/dockera zamiast klienta (wspólne limity na IP)."""
from app.routers import portal


def test_whoami_reports_public_client_ip(client, monkeypatch):
    monkeypatch.setattr(portal, "client_ip", lambda request: "8.8.8.8")
    assert client.get("/api/public/whoami").json() == {"ip": "8.8.8.8", "private": False}


def test_whoami_flags_proxy_address(client, monkeypatch):
    monkeypatch.setattr(portal, "client_ip", lambda request: "172.18.0.3")
    assert client.get("/api/public/whoami").json()["private"] is True


def test_whoami_without_login_and_garbage_ip(client):
    r = client.get("/api/public/whoami")   # TestClient: host „testclient” — nie IP
    assert r.status_code == 200 and r.json()["private"] is True
