"""Push ntfy o nowym gościu bramki demo: tylko po udanym zapisie, w tle, błąd nie szkodzi gościowi."""
import httpx
import pytest

from app import visitor_notify
from app.config import settings
from app.models import Role, User
from app.security import hash_password

GOOD = {"first_name": "Jan", "last_name": "Żółć", "company": "ACME Sp. z o.o.", "consent": True}
URL = "https://ntfy.example/tajny-temat"


@pytest.fixture
def gate(db_session, monkeypatch):
    monkeypatch.setattr(settings, "demo_readonly_logins", "demo")
    monkeypatch.setattr(settings, "demo_visitor_gate", True)
    monkeypatch.setattr(settings, "ntfy_url", URL)
    monkeypatch.setattr(settings, "ntfy_token", "")
    monkeypatch.setattr(settings, "ntfy_watch_companies", "")
    db_session.add(User(login="demo", full_name="Demo", role=Role.warehouse,
                        hashed_password=hash_password("demopass1"), is_active=True))
    db_session.commit()


@pytest.fixture
def sent(monkeypatch):
    """Wątek uruchamiany synchronicznie, httpx.post zamockowany — zero ruchu sieciowego."""
    calls: list[dict] = []

    def fake_post(url, content, headers, timeout):
        calls.append({"url": url, "body": content.decode("utf-8"), "headers": headers, "timeout": timeout})
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr(visitor_notify, "_start", lambda target, *args: target(*args))
    monkeypatch.setattr(visitor_notify.httpx, "post", fake_post)
    return calls


def test_valid_form_sends_one_push(client, gate, sent):
    assert client.post("/api/public/demo-visitor", json=GOOD).status_code == 204
    assert len(sent) == 1
    call = sent[0]
    assert call["url"] == URL
    assert call["body"] == "Jan Żółć (ACME Sp. z o.o.) wszedł do container-queue"
    assert call["headers"]["Title"] == "Nowy gosc: container-queue"
    assert call["headers"]["Tags"] == "bell" and call["headers"]["Priority"] == "high"
    assert "Authorization" not in call["headers"]
    assert call["timeout"] == 5
    for name, value in call["headers"].items():
        assert value.isascii(), name


@pytest.mark.parametrize("patch, code", [
    ({"website": "http://spam"}, 400), ({"consent": False}, 422), ({"last_name": "K"}, 422),
])
def test_rejected_form_sends_nothing(client, gate, sent, patch, code):
    assert client.post("/api/public/demo-visitor", json={**GOOD, **patch}).status_code == code
    assert sent == []


def test_no_url_means_no_push(client, gate, sent, monkeypatch):
    monkeypatch.setattr(settings, "ntfy_url", "")
    assert client.post("/api/public/demo-visitor", json=GOOD).status_code == 204
    assert sent == []


def test_token_adds_bearer_header(client, gate, sent, monkeypatch):
    monkeypatch.setattr(settings, "ntfy_token", "tk_abc")
    assert client.post("/api/public/demo-visitor", json=GOOD).status_code == 204
    assert sent[0]["headers"]["Authorization"] == "Bearer tk_abc"


def test_send_failure_does_not_break_visitor(client, gate, monkeypatch, caplog):
    def boom(*args, **kwargs):
        raise httpx.ConnectError("brak sieci")

    monkeypatch.setattr(visitor_notify, "_start", lambda target, *args: target(*args))
    monkeypatch.setattr(visitor_notify.httpx, "post", boom)
    r = client.post("/api/public/demo-visitor", json=GOOD)
    assert r.status_code == 204 and "demo_visitor" in r.headers["set-cookie"]
    assert "ntfy" in caplog.text
    login = client.post("/api/auth/login", data={"username": "demo", "password": "demopass1"})
    assert login.status_code == 200


def test_body_truncated_to_300_chars(monkeypatch, sent):
    monkeypatch.setattr(settings, "ntfy_url", URL)
    visitor_notify.notify_visitor("A" * 100, "B" * 100, "C" * 100)
    assert len(sent[0]["body"]) == 300


def test_runs_in_daemon_thread(monkeypatch):
    started = []

    class FakeThread:
        def __init__(self, target, args, daemon, name):
            started.append(daemon)

        def start(self):
            pass

    monkeypatch.setattr(settings, "ntfy_url", URL)
    monkeypatch.setattr(visitor_notify.threading, "Thread", FakeThread)
    visitor_notify.notify_visitor("Jan", "Kowalski", "ACME")
    assert started == [True]


@pytest.mark.parametrize("bad", ["file:///etc/passwd", "ftp://ntfy.example/t", "ntfy.sh/temat"])
def test_non_http_url_is_skipped(monkeypatch, sent, caplog, bad):
    monkeypatch.setattr(settings, "ntfy_url", bad)
    visitor_notify.notify_visitor("Jan", "Kowalski", "ACME")
    assert sent == []
    assert "NTFY_URL" in caplog.text


# --- A. alarm „uwaga, ta firma” (NTFY_WATCH_COMPANIES; w testach tylko fikcyjne frazy) ---

def test_watched_company_sends_urgent_alarm(client, gate, sent, monkeypatch):
    monkeypatch.setattr(settings, "ntfy_watch_companies", "globex, acme")
    assert client.post("/api/public/demo-visitor", json=GOOD).status_code == 204
    call = sent[0]
    assert call["headers"]["Priority"] == "urgent"
    assert call["headers"]["Tags"] == "rotating_light"
    assert call["headers"]["Title"] == "UWAGA firma z listy: container-queue"
    assert call["body"] == "⚠️ Jan Żółć (ACME Sp. z o.o.) wszedł do container-queue"
    for name, value in call["headers"].items():
        assert value.isascii(), name


@pytest.mark.parametrize("company, phrases, watched", [
    ("ÄCME sp. z o.o.", "acme", True),
    ("Łódzka  Hurtownia", "lodzka hurtownia", True),
    ("Firma Zupełnie Inna", "acme, globex", False),
    ("ACME", "", False),
    ("ACME", " , a ,", False),          # puste i 1-znakowe frazy nic nie łapią
])
def test_watch_matching(monkeypatch, company, phrases, watched):
    monkeypatch.setattr(settings, "ntfy_watch_companies", phrases)
    assert visitor_notify.is_watched(company) is watched


@pytest.mark.parametrize("phrases", ["", "globex"])
def test_unwatched_company_keeps_normal_push(client, gate, sent, monkeypatch, phrases):
    monkeypatch.setattr(settings, "ntfy_watch_companies", phrases)
    assert client.post("/api/public/demo-visitor", json=GOOD).status_code == 204
    headers = sent[0]["headers"]
    assert (headers["Priority"], headers["Tags"]) == ("high", "bell")
    assert not sent[0]["body"].startswith("⚠️")


def test_watched_without_url_sends_nothing(client, gate, sent, monkeypatch):
    monkeypatch.setattr(settings, "ntfy_watch_companies", "acme")
    monkeypatch.setattr(settings, "ntfy_url", "")
    assert client.post("/api/public/demo-visitor", json=GOOD).status_code == 204
    assert sent == []
