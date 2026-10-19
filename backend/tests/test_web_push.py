"""Powiadomienia push (czwarta lista PO, pkt 2, US-086)."""
import base64

import http_ece
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from app import web_push
from app.config import settings
from app.database import SessionLocal
from app.models import User
from app.notifications import notify

FCM = "https://fcm.googleapis.com/fcm/send/abc123"


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


@pytest.fixture
def vapid(monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    monkeypatch.setattr(settings, "vapid_private_key", _b64(key.private_numbers().private_value.to_bytes(32, "big")))
    return key


def _browser():
    """Klucze przeglądarki: p256dh (publiczny ECDH) + auth (16 bajtów)."""
    key = ec.generate_private_key(ec.SECP256R1())
    pub = key.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    auth = b"0123456789abcdef"
    return key, {"endpoint": FCM, "p256dh": _b64(pub), "auth": _b64(auth)}, auth


def test_endpoint_allowlist_blocks_ssrf():
    assert web_push.allowed_endpoint(FCM)
    assert web_push.allowed_endpoint("https://web.push.apple.com/QAbc")
    assert web_push.allowed_endpoint("https://updates.push.services.mozilla.com/wpush/v2/x")
    for bad in ("http://fcm.googleapis.com/x", "https://localhost/x", "https://169.254.169.254/latest",
                "https://fcm.googleapis.com.evil.pl/x", "https://evilpush.apple.com.pl/x",
                "https://fcm.googleapis.com:8443/x"):
        assert not web_push.allowed_endpoint(bad), bad


def test_disabled_without_key(monkeypatch):
    monkeypatch.setattr(settings, "vapid_private_key", "")
    assert web_push.public_key() is None


def test_payload_encrypted_for_browser_and_signed(vapid, monkeypatch):
    browser_key, sub, auth = _browser()
    body = web_push.encrypt(sub, b'{"title":"x"}')
    assert http_ece.decrypt(body, private_key=browser_key, auth_secret=auth, version="aes128gcm") == b'{"title":"x"}'

    header = web_push._vapid_header(FCM, vapid)
    token = header.split("t=")[1].split(",")[0]
    claims = jwt.decode(token, vapid.public_key(), algorithms=["ES256"], audience="https://fcm.googleapis.com")
    assert claims["sub"] == settings.vapid_subject
    assert header.endswith(f"k={web_push.public_key()}")


def test_subscribe_validates_and_caps_devices(client, vapid):
    _, sub, _ = _browser()
    with SessionLocal() as db:
        uid = db.query(User).filter_by(login="admin").one().id
        with pytest.raises(ValueError):
            web_push.subscribe(db, uid, "https://127.0.0.1/x", sub["p256dh"], sub["auth"])
        with pytest.raises(ValueError):
            web_push.subscribe(db, uid, FCM, sub["p256dh"], "krotki")
        for i in range(web_push.MAX_SUBS + 2):
            web_push.subscribe(db, uid, f"{FCM}{i}", sub["p256dh"], sub["auth"])
        subs = web_push.load(db, uid)
        assert len(subs) == web_push.MAX_SUBS and subs[0]["endpoint"] == f"{FCM}{web_push.MAX_SUBS + 1}"
        web_push.unsubscribe(db, uid, subs[0]["endpoint"])
        assert len(web_push.load(db, uid)) == web_push.MAX_SUBS - 1
        web_push.unsubscribe(db, uid)
        assert web_push.load(db, uid) == []
        db.rollback()


def test_notify_pushes_only_urgent_kinds_after_commit(client, vapid, monkeypatch):
    _, sub, _ = _browser()
    sent: list[tuple[str, dict]] = []
    monkeypatch.setattr(web_push, "send", lambda s, payload: sent.append((s["endpoint"], payload)) or 201)
    monkeypatch.setattr("app.notifications._submit", lambda fn, *a, **kw: fn(*a, **kw))
    with SessionLocal() as db:
        admin = db.query(User).filter_by(login="admin").one()
        web_push.subscribe(db, admin.id, FCM, sub["p256dh"], sub["auth"])
        db.commit()
        notify(db, [admin], kind="status", title="zwykła zmiana statusu", broadcast=False)
        notify(db, [admin], kind="demurrage", title="Demurrage MSKU1234565", container_id=7, broadcast=False)
        assert sent == []                                   # nic przed commitem
        db.commit()
        web_push.unsubscribe(db, admin.id)
        db.commit()
    assert sent == [(FCM, {"title": "Demurrage MSKU1234565", "url": "/kontenery/7", "tag": "demurrage-7"})]


def test_gone_device_is_removed(client, vapid, monkeypatch):
    _, sub, _ = _browser()
    monkeypatch.setattr(web_push, "send", lambda s, payload: 410)
    with SessionLocal() as db:
        uid = db.query(User).filter_by(login="admin").one().id
        web_push.subscribe(db, uid, FCM, sub["p256dh"], sub["auth"])
        db.commit()
    web_push._deliver([(uid, {**sub})], {"title": "x"})
    with SessionLocal() as db:
        assert web_push.load(db, uid) == []


def test_endpoints(client, admin_headers, vapid, monkeypatch):
    _, sub, _ = _browser()
    r = client.get("/api/notifications/push", headers=admin_headers)
    assert r.status_code == 200 and r.json()["available"] and r.json()["endpoints"] == []
    assert "demurrage" in r.json()["kinds"]
    bad = client.post("/api/notifications/push", headers=admin_headers,
                      json={**sub, "endpoint": "https://intranet.local/hook"})
    assert bad.status_code == 422
    assert client.post("/api/notifications/push", headers=admin_headers, json=sub).status_code == 200
    monkeypatch.setattr(web_push, "send", lambda s, payload: 201)
    assert client.post("/api/notifications/push/test", headers=admin_headers).json() == {"devices": 1, "sent": 1}
    assert client.post("/api/notifications/push/remove", headers=admin_headers, json={"endpoint": FCM}).status_code == 200
    assert client.get("/api/notifications/push", headers=admin_headers).json()["endpoints"] == []
    monkeypatch.setattr(settings, "vapid_private_key", "")
    assert client.post("/api/notifications/push", headers=admin_headers, json=sub).status_code == 409

