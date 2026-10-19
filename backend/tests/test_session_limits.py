"""Limity sesji (ASVS 3.3.2, decyzja PO 2026-10-19): 30 min bezczynności, 12 h od zalogowania."""
import datetime

import jwt

from app import session_limits
from app.config import settings
from app.security import ALGORITHM


def _claims(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])


def _login(client) -> dict:
    return client.post("/api/auth/login", data={"username": "admin", "password": "admin123"}).json()


def _life(claims: dict) -> int:
    return int(claims["exp"]) - int(claims["iat"])


def test_tokens_live_within_idle_window(client):
    tokens = _login(client)
    access, refresh = _claims(tokens["access_token"]), _claims(tokens["refresh_token"])
    assert _life(refresh) <= settings.session_idle_minutes * 60
    assert _life(access) <= settings.session_idle_minutes * 60 // 2
    assert abs(refresh["at"] - refresh["iat"]) <= 2          # czas zalogowania w refresh


def test_rotation_keeps_login_time(client):
    tokens = _login(client)
    started = _claims(tokens["refresh_token"])["at"]
    rotated = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert rotated.status_code == 200
    assert _claims(rotated.json()["refresh_token"])["at"] == started


def test_refresh_refused_after_max_hours(client, monkeypatch):
    tokens = _login(client)
    later = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=settings.session_max_hours,
                                                                     minutes=1)
    monkeypatch.setattr(session_limits, "_now", lambda: later)
    r = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 401 and "zaloguj" in r.json()["detail"]


def test_tokens_never_outlive_max_hours(monkeypatch):
    start = datetime.datetime.now(datetime.UTC)
    monkeypatch.setattr(session_limits, "_now",
                        lambda: start + datetime.timedelta(hours=settings.session_max_hours, minutes=-5))
    assert session_limits.refresh_lifetime(start) <= datetime.timedelta(minutes=5)
    assert session_limits.access_lifetime(start) <= datetime.timedelta(minutes=5)


def test_legacy_token_without_login_time_counts_from_iat():
    assert session_limits.session_start({"iat": 1_700_000_000}).timestamp() == 1_700_000_000
    assert session_limits.session_start({"iat": 1, "at": 5}).timestamp() == 5
