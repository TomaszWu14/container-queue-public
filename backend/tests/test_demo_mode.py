"""Instancja portfolio: konto demo tylko do odczytu (egzekwowane w API), podpowiedź logowania,
bezpieczniki skryptu scripts/seed_demo.py (kasuje wszystko — tylko na instancji pokazowej, z flagą)."""
import datetime as dt

import pytest

from app.config import settings
from app.models import Role, User
from app.security import hash_password
from scripts import seed_demo

from .conftest import login

PW = "Demo-Portfolio-2026"


def test_demo_account_reads_but_cannot_write(client, db_session, monkeypatch, admin_headers):
    monkeypatch.setattr(settings, "demo_readonly_logins", "demo")
    db_session.add(User(login="demo", hashed_password=hash_password(PW), role=Role.logistics,
                        view_all_companies=True))
    db_session.commit()
    hdr = login(client, "demo", PW)
    assert client.get("/api/containers", headers=hdr).status_code == 200
    r = client.patch("/api/auth/me/settings", headers=hdr, json={"language": "en"})
    assert r.status_code == 403 and "demo" in r.json()["detail"]
    assert client.post("/api/containers", headers=hdr, json={"container_no": "MSKU1234565"}).status_code == 403
    assert client.post("/api/auth/logout", headers=hdr).status_code in (200, 204)
    # zwykłe konto na tej samej instancji zapisuje normalnie
    assert client.patch("/api/auth/me/settings", headers=admin_headers,
                        json={"language": "pl"}).status_code != 403


def test_branding_exposes_demo_hint_only_when_set(client, monkeypatch):
    assert client.get("/api/public/branding").json()["demo_hint"] == ""
    monkeypatch.setattr(settings, "demo_login_hint", "demo / Demo-Portfolio-2026")
    assert client.get("/api/public/branding").json()["demo_hint"] == "demo / Demo-Portfolio-2026"


def test_seed_refuses_without_demo_instance_or_flag(monkeypatch):
    monkeypatch.setattr(settings, "demo_readonly_logins", "")
    with pytest.raises(SystemExit, match="nie jest instancja pokazowa"):
        seed_demo.check_guards(["--wyczysc-wszystko"])
    monkeypatch.setattr(settings, "demo_readonly_logins", "demo")
    with pytest.raises(SystemExit, match="brak flagi"):
        seed_demo.check_guards([])
    assert seed_demo.check_guards(["--wyczysc-wszystko"]) == ["demo"]


def _add_demo(db_session, monkeypatch):
    monkeypatch.setattr(settings, "demo_readonly_logins", "demo")
    db_session.add(User(login="demo", hashed_password=hash_password(PW), role=Role.logistics,
                        view_all_companies=True))
    db_session.commit()


def test_demo_logout_keeps_other_demo_sessions(client, db_session, monkeypatch):
    # wspólne konto demo: wylogowanie jednej osoby nie zrywa sesji pozostałych
    _add_demo(db_session, monkeypatch)
    first, second = login(client, "demo", PW), login(client, "demo", PW)
    assert client.post("/api/auth/logout", headers=first).status_code == 204
    assert client.get("/api/auth/me", headers=second).status_code == 200


def test_demo_account_not_locked_by_distributed_failures(client, db_session, monkeypatch):
    # rozproszone złe hasła (każde z innego IP) nie odcinają demo innym — zwykłe konto tak
    import itertools

    from app.routers import auth
    _add_demo(db_session, monkeypatch)
    ips = (f"203.0.113.{i}" for i in itertools.count(1))
    monkeypatch.setattr(auth, "_client_ip", lambda _request: next(ips))
    bad = {"username": "demo", "password": "zle-haslo-123"}
    for _ in range(settings.login_account_lock_after + 2):
        assert client.post("/api/auth/login", data=bad).status_code == 401
    assert client.post("/api/auth/login",
                       data={"username": "demo", "password": PW}).status_code == 200


def test_branding_exposes_demo_account_and_support_only_on_demo_instance(client, monkeypatch):
    body = client.get("/api/public/branding").json()
    assert body["demo_login"] == "" and body["demo_password"] == "" and body["support_email"] == ""
    monkeypatch.setattr(settings, "demo_password", PW)      # samo hasło bez loginów demo → nic
    assert client.get("/api/public/branding").json()["demo_password"] == ""
    monkeypatch.setattr(settings, "demo_readonly_logins", "demo, gosc")
    monkeypatch.setattr(settings, "support_email", "autor@example.org")
    body = client.get("/api/public/branding").json()
    assert (body["demo_login"], body["demo_password"]) == ("demo", PW)
    assert body["support_email"] == "autor@example.org"


def test_me_flags_demo_account(client, db_session, monkeypatch, admin_headers):
    _add_demo(db_session, monkeypatch)
    assert client.get("/api/auth/me", headers=login(client, "demo", PW)).json()["is_demo"] is True
    assert client.get("/api/auth/me", headers=admin_headers).json()["is_demo"] is False


def test_seed_gives_recruiter_a_full_first_screen(client, monkeypatch, tmp_path):
    # demo dla rekrutera: kolejka w bieżącym tygodniu niepusta, statusy zgodne z datami,
    # historia zmian na karcie kontenera, punkty na mapie śledzenia
    import datetime as dt

    from app.database import SessionLocal
    from app.models import AuditLog, Container, TrackingEvent
    from app.models.enums import ContainerStatus, today_pl
    monkeypatch.setattr(settings, "demo_readonly_logins", "demo")
    monkeypatch.setattr(settings, "uploads_dir", str(tmp_path))   # dokumenty demo (US-027)
    seed_demo.wipe()
    assert seed_demo.seed(["demo"], PW) == 150
    today = today_pl()
    with SessionLocal() as db:
        cs = db.query(Container).all()
        week = [c for c in cs if c.notify_date and 0 <= (c.notify_date - today).days < 7]
        assert len(week) >= 10
        assert all(c.eta > today for c in cs if c.status == ContainerStatus.ZAPOWIEDZIANY)
        assert all(c.eta < today for c in cs if c.status == ContainerStatus.ZREALIZOWANY)
        assert db.query(AuditLog).filter_by(entity_type="containers", field="status").count() > 300
        # 45 zdarzeń mapy śledzenia + wyładunki z historii przypłynięć (punktualność armatorów, US-071)
        assert db.query(TrackingEvent).count() > 45
        assert all(e.occurred_at < dt.datetime.now() for e in db.query(TrackingEvent))
    hdr = login(client, "demo", PW)
    assert len(client.get("/api/tracking/map", headers=hdr).json()["points"]) == 45


def test_demo_presence_ping_allowed(client, db_session, monkeypatch):
    # obecność „online” (stan w pamięci) nie jest zapisem danych — bez 403 w konsoli demo
    _add_demo(db_session, monkeypatch)
    hdr = login(client, "demo", PW)
    assert client.post("/api/presence", headers=hdr, json={"path": "/kolejka", "active": True}).status_code == 200
    assert client.post("/api/presence/leave", headers=hdr).status_code == 204


def test_seed_on_start_skips_fresh_data_and_keeps_sessions(client, monkeypatch, tmp_path):
    # restart kontenera demo (każde wdrożenie) nie kasuje aktualnych danych ani sesji odwiedzających
    from app.database import SessionLocal
    from app.models import RefreshToken
    monkeypatch.setattr(settings, "demo_readonly_logins", "demo")
    monkeypatch.setattr(settings, "uploads_dir", str(tmp_path))
    monkeypatch.setenv("DEMO_PASSWORD", PW)
    args = ["--wyczysc-wszystko", "--tylko-gdy-nieaktualne"]
    seed_demo.main(args)   # pierwsze wgranie (brak znacznika)
    login(client, "demo", PW)
    with SessionLocal() as db:
        sessions = db.query(RefreshToken).count()
    assert sessions >= 1
    seed_demo.main(args)   # restart: dane z dziś, te same skrypty — pominięte
    with SessionLocal() as db:
        assert db.query(RefreshToken).count() == sessions
    monkeypatch.setattr(seed_demo, "today_pl", lambda: dt.date(2000, 1, 1))
    seed_demo.main(args)   # inny dzień — dane nieaktualne, wgrane od nowa (sesje znikają)
    with SessionLocal() as db:
        assert db.query(RefreshToken).count() == 0


def test_seed_stamp_changes_with_password():
    assert seed_demo.seed_stamp(["demo"], PW) != seed_demo.seed_stamp(["demo"], PW + "x")


def test_demo_token_reuse_does_not_log_out_other_visitors(client, db_session, monkeypatch):
    # wspólne konto demo: powtórzony stary refresh token jednej osoby (np. telefon zgubił
    # odpowiedź) nie może zrywać sesji wszystkich odwiedzających
    import datetime as _dt

    from app.database import SessionLocal
    from app.models import RefreshToken
    _add_demo(db_session, monkeypatch)
    first = client.post("/api/auth/login", data={"username": "demo", "password": PW}).json()
    other = login(client, "demo", PW)
    old = first["refresh_token"]
    assert client.post("/api/auth/refresh", json={"refresh_token": old}).status_code == 200
    with SessionLocal() as db:   # odwołanie starsze niż okno łaski
        for row in db.query(RefreshToken).filter(RefreshToken.revoked_at.isnot(None)):
            row.revoked_at -= _dt.timedelta(seconds=3600)
        db.commit()
    assert client.post("/api/auth/refresh", json={"refresh_token": old}).status_code == 401
    assert client.get("/api/auth/me", headers=other).status_code == 200
