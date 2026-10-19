"""Sekret TOTP szyfrowany w bazie (ASVS 2.8.2, US-092)."""
from app import crypto
from app.database import SessionLocal
from app.models import User
from app.security import totp
from tests.conftest import login


def _enable(client, headers) -> str:
    secret = client.post("/api/auth/2fa/setup", headers=headers).json()["secret"]
    r = client.post("/api/auth/2fa/enable", headers=headers, json={"secret": secret, "code": totp(secret)})
    assert r.status_code == 200, r.text
    return secret


def _stored(login_name: str) -> str:
    with SessionLocal() as db:
        return db.query(User).filter_by(login=login_name).one().totp_secret


def _login_2fa(client, login_name: str, password: str, secret: str):
    first = client.post("/api/auth/login", data={"username": login_name, "password": password}).json()
    assert first.get("totp_required") is True
    return client.post("/api/auth/2fa/verify",
                       json={"pending_token": first["pending_token"], "code": totp(secret)})


def _user(client, admin_headers, name: str) -> dict:
    assert client.post("/api/users", headers=admin_headers, json={
        "login": name, "password": "haslo1234", "role": "logistics",
        "view_all_companies": True}).status_code == 201
    return login(client, name, "haslo1234")


def test_secret_stored_encrypted_and_login_works(client, admin_headers):
    secret = _enable(client, _user(client, admin_headers, "totp.enc1"))
    stored = _stored("totp.enc1")
    assert stored.startswith("enc:") and secret not in stored
    assert crypto.decrypt(stored) == secret
    assert _login_2fa(client, "totp.enc1", "haslo1234", secret).status_code == 200


def test_plain_legacy_secret_still_works_and_gets_encrypted(client, admin_headers):
    secret = _enable(client, _user(client, admin_headers, "totp.enc2"))
    with SessionLocal() as db:                         # wpis jak sprzed migracji
        db.query(User).filter_by(login="totp.enc2").one().totp_secret = secret
        db.commit()
    assert _login_2fa(client, "totp.enc2", "haslo1234", secret).status_code == 200
    assert crypto.decrypt(_stored("totp.enc2")) == secret and _stored("totp.enc2").startswith("enc:")


def test_undecryptable_secret_rejects_code_without_crash(client, admin_headers):
    secret = _enable(client, _user(client, admin_headers, "totp.enc3"))
    with SessionLocal() as db:
        db.query(User).filter_by(login="totp.enc3").one().totp_secret = "enc:zepsuty"
        db.commit()
    assert _login_2fa(client, "totp.enc3", "haslo1234", secret).status_code == 401
