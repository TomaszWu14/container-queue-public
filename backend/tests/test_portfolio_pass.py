"""Przepustka z portfolio: ciasteczko `gosc` wpuszcza na demo bez formularza (portfolio mockowane)."""
import httpx
import pytest

from app import portfolio_pass, visitor_notify
from app.config import settings
from app.models import Role, User
from app.security import hash_password


class _Resp:
    def __init__(self, code):
        self.status_code = code


@pytest.fixture
def gate(db_session, monkeypatch):
    monkeypatch.setattr(settings, "demo_readonly_logins", "demo")
    monkeypatch.setattr(settings, "demo_visitor_gate", True)
    monkeypatch.setattr(settings, "portfolio_pass", True)
    monkeypatch.setattr(settings, "portfolio_url", "https://portfolio.test")
    portfolio_pass.clear_cache()
    db_session.add(User(login="demo", full_name="Demo", role=Role.warehouse,
                        hashed_password=hash_password("demopass1"), is_active=True))
    db_session.commit()
    calls = []
    monkeypatch.setattr(visitor_notify, "notify_visitor", lambda *a, **k: calls.append(("ntfy", a)))
    return calls


def _mock(monkeypatch, result):
    seen = []

    def fake_get(url, **kw):
        seen.append((url, kw))
        if isinstance(result, Exception):
            raise result
        return _Resp(result)

    monkeypatch.setattr(portfolio_pass.httpx, "get", fake_get)
    return seen


def _login(client, cookie="tok123"):
    if cookie:
        client.cookies.set("gosc", cookie)
    return client.post("/api/auth/login", data={"username": "demo", "password": "demopass1"})


def test_valid_pass_skips_form_and_sends_only_gosc_cookie(client, gate, monkeypatch):
    seen = _mock(monkeypatch, 200)
    client.cookies.set("inne", "x")
    assert _login(client).status_code == 200
    url, kw = seen[0]
    assert url == "https://portfolio.test/api/gosc"
    assert kw["headers"] == {"Cookie": "gosc=tok123"}
    assert kw["timeout"] == 2.0 and kw["follow_redirects"] is False
    assert gate == []   # brak własnego pusha


def test_positive_result_is_cached(client, gate, monkeypatch):
    seen = _mock(monkeypatch, 200)
    assert _login(client).status_code == 200
    assert _login(client).status_code == 200
    assert len(seen) == 1


@pytest.mark.parametrize("result", [401, 500, 302, httpx.ReadTimeout("t"), RuntimeError("x")])
def test_refusal_or_error_keeps_form(client, gate, monkeypatch, result):
    _mock(monkeypatch, result)
    assert _login(client).status_code == 428


def test_no_cookie_no_network_call(client, gate, monkeypatch):
    seen = _mock(monkeypatch, 200)
    assert _login(client, cookie=None).status_code == 428
    assert seen == []


def test_oversized_cookie_and_disabled_pass_make_no_call(client, gate, monkeypatch):
    seen = _mock(monkeypatch, 200)
    assert _login(client, cookie="a" * 201).status_code == 428
    monkeypatch.setattr(settings, "portfolio_pass", False)
    assert _login(client).status_code == 428
    assert seen == []


def test_non_https_url_disables_check(client, gate, monkeypatch):
    seen = _mock(monkeypatch, 200)
    monkeypatch.setattr(settings, "portfolio_url", "http://portfolio.test")
    assert _login(client).status_code == 428
    assert seen == []
