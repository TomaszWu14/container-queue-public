"""Kody zapasowe 2FA: solone, wolne hashe i zgodność ze starymi kodami (US-088, ASVS 2.6.2/2.6.3)."""
import hashlib
import json
import re

from app.backup_codes import generate_backup_codes, hash_backup_code, match_backup_code


def test_codes_are_long_unambiguous_and_unique():
    codes = generate_backup_codes()
    assert len(codes) == len(set(codes)) == 10
    for code in codes:
        assert re.fullmatch(r"[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}", code)   # bez 0/O, 1/I


def test_hash_is_salted_and_slow():
    code = generate_backup_codes(1)[0]
    a, b = hash_backup_code(code), hash_backup_code(code)
    assert a != b and a.startswith("s1$")                         # inna sól za każdym razem
    assert code.replace("-", "") not in a
    assert match_backup_code(code, [a]) == a
    # wpisywanie bez myślnika / małymi literami / ze spacjami też działa
    assert match_backup_code(" " + code.replace("-", "").lower() + " ", [a]) == a
    assert match_backup_code("AAAA-BBBB-CCCC", [a]) is None


def test_legacy_unsalted_codes_still_work_once():
    old = "a1b2c3d4e5"
    stored = [hashlib.sha256(old.encode()).hexdigest(), hash_backup_code("ZZZZ-ZZZZ-ZZZZ")]
    assert match_backup_code(old, stored) == stored[0]
    assert match_backup_code("nie-ten", stored) is None


def test_login_with_new_backup_code_consumes_it(client):
    from tests.test_w14_security import _enable_2fa, login
    from app.database import SessionLocal
    from app.models import User
    headers = login(client)
    _, codes = _enable_2fa(client, headers)
    pending = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"}).json()["pending_token"]  # gitleaks:allow
    ok = client.post("/api/auth/2fa/verify", json={"pending_token": pending, "code": codes[0].lower()})
    assert ok.status_code == 200, ok.text
    with SessionLocal() as db:
        left = json.loads(db.query(User).filter_by(login="admin").one().totp_backup_codes)
    assert len(left) == 9 and all(h.startswith("s1$") for h in left)
    pending = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"}).json()["pending_token"]  # gitleaks:allow
    again = client.post("/api/auth/2fa/verify", json={"pending_token": pending, "code": codes[0]})
    assert again.status_code == 401                                 # jednorazowy
