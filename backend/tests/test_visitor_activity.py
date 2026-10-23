"""Aktywność gościa demo: sygnał ekranu z SPA, sekcje, limit, próg pushu, lista admina."""
import datetime

import httpx
import jwt
import pytest
from sqlalchemy import select

from app import visitor_activity, visitor_notify
from app.config import settings
from app.models import DemoVisitor, utcnow

GOOD = {"first_name": "Jan", "last_name": "Kowalski", "company": "Firma Testowa", "consent": True}
URL = "https://ntfy.example/tajny-temat"
VIEW = "/api/public/demo-visitor/view"


@pytest.fixture
def gate(monkeypatch):
    monkeypatch.setattr(settings, "demo_readonly_logins", "demo")
    monkeypatch.setattr(settings, "demo_visitor_gate", True)
    monkeypatch.setattr(settings, "ntfy_url", "")
    monkeypatch.setattr(settings, "ntfy_watch_companies", "")
    monkeypatch.setattr(settings, "ntfy_engaged_views", 10)


@pytest.fixture
def sent(monkeypatch):
    calls: list[dict] = []

    def fake_post(url, content, headers, timeout):
        calls.append({"body": content.decode("utf-8"), "headers": headers})
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr(settings, "ntfy_url", URL)
    monkeypatch.setattr(visitor_notify, "_start", lambda target, *args: target(*args))
    monkeypatch.setattr(visitor_notify.httpx, "post", fake_post)
    return calls


def _enter(client) -> None:
    assert client.post("/api/public/demo-visitor", json=GOOD).status_code == 204


def _row(db_session) -> DemoVisitor:
    db_session.expire_all()
    return db_session.scalars(select(DemoVisitor)).one()


def test_three_screens_are_counted(client, gate, db_session):
    _enter(client)
    for path in ("/kolejka/123", "/kolejka", "/"):
        assert client.post(VIEW, json={"path": path}).status_code == 204
    row = _row(db_session)
    assert row.page_views == 3
    assert row.sections == {"kolejka": 2, "start": 1}
    assert row.last_seen_at is not None and row.last_seen_at >= row.created_at


@pytest.mark.parametrize("path", [
    "/api/containers", "/assets/index-abc.js", "/health", "/static/x.css", "/Ünicode",
    "/a b", "kolejka", "//evil.example/x", "/favicon.ico",
])
def test_technical_or_invalid_paths_not_counted(client, gate, db_session, path):
    _enter(client)
    assert client.post(VIEW, json={"path": path}).status_code == 204
    assert client.get("/api/health").status_code == 200   # zwykłe GET-y API też nic nie liczą
    assert _row(db_session).page_views == 0


def test_section_trimmed_to_40_chars():
    assert visitor_activity.section_of("/" + "a" * 60 + "/x?y=1") == "a" * 40
    assert visitor_activity.section_of("/Master-Data?tab=1#x") == "master-data"


def test_without_cookie_not_counted(client, gate, db_session):
    _enter(client)
    client.cookies.clear()
    assert client.post(VIEW, json={"path": "/kolejka"}).status_code == 204
    assert _row(db_session).page_views == 0


@pytest.mark.parametrize("token_of", [
    lambda vid: jwt.encode({"sub": str(vid), "typ": "demo_visitor"}, "inny-klucz-" + "x" * 32, algorithm="HS256"),
    lambda vid: jwt.encode({"sub": str(vid), "typ": "access"}, settings.secret_key, algorithm="HS256"),
    lambda vid: "nie-token",
])
def test_forged_cookie_not_counted(client, gate, db_session, token_of):
    _enter(client)
    vid = _row(db_session).id
    client.cookies.clear()
    client.cookies.set("demo_visitor", token_of(vid))
    assert client.post(VIEW, json={"path": "/kolejka"}).status_code == 204
    assert _row(db_session).page_views == 0


def test_engaged_threshold_sends_exactly_one_push(client, gate, db_session, sent, monkeypatch):
    monkeypatch.setattr(settings, "ntfy_engaged_views", 3)
    _enter(client)
    sent.clear()   # push o wejściu nie jest tematem tego testu
    for _ in range(5):
        client.post(VIEW, json={"path": "/kolejka"})
    assert len(sent) == 1
    call = sent[0]
    assert call["body"] == "Jan Kowalski (Firma Testowa) obejrzał już 3 ekranów w container-queue"
    assert call["headers"]["Title"] == "Gosc oglada demo: container-queue"
    assert call["headers"]["Tags"] == "eyes" and call["headers"]["Priority"] == "default"


def test_engaged_push_urgent_for_watched_company(client, gate, db_session, sent, monkeypatch):
    monkeypatch.setattr(settings, "ntfy_engaged_views", 1)
    monkeypatch.setattr(settings, "ntfy_watch_companies", "testowa")
    _enter(client)
    sent.clear()
    client.post(VIEW, json={"path": "/kolejka"})
    assert [c["headers"]["Priority"] for c in sent] == ["urgent"]


def test_engaged_zero_disables_push(client, gate, db_session, sent, monkeypatch):
    monkeypatch.setattr(settings, "ntfy_engaged_views", 0)
    _enter(client)
    sent.clear()
    for _ in range(12):
        client.post(VIEW, json={"path": "/kolejka"})
    assert sent == [] and _row(db_session).page_views == 12


def test_counting_error_does_not_break_response(client, gate, db_session, monkeypatch, caplog):
    _enter(client)

    def boom(*args, **kwargs):
        raise RuntimeError("baza padła")

    monkeypatch.setattr(visitor_activity, "_bump", boom)
    assert client.post(VIEW, json={"path": "/kolejka"}).status_code == 204
    assert "aktywności gościa demo" in caplog.text


def test_sections_limited_to_20(client, gate, db_session):
    _enter(client)
    for i in range(25):
        client.post(VIEW, json={"path": f"/sekcja{i}"})
    client.post(VIEW, json={"path": "/sekcja0"})
    row = _row(db_session)
    assert row.page_views == 26
    assert len(row.sections) == 20 and row.sections["sekcja0"] == 2 and "sekcja24" not in row.sections


def test_admin_list_and_csv_show_activity(client, gate, db_session, admin_headers):
    t = utcnow()
    db_session.add_all([
        DemoVisitor(first_name="A", last_name="Aktywny", company="F1", created_at=t - datetime.timedelta(minutes=30),
                    page_views=7, last_seen_at=t - datetime.timedelta(minutes=18),
                    sections={"kolejka": 4, "pulpit": 1, "sledzenie": 2, "kalendarz": 1}),
        DemoVisitor(first_name="B", last_name="Bierny", company="F2", created_at=t)])
    db_session.commit()
    rows = {r["first_name"]: r for r in client.get("/api/admin/demo-visitors", headers=admin_headers).json()}
    assert rows["A"]["page_views"] == 7 and rows["A"]["duration_min"] == 12
    assert rows["A"]["top_sections"] == ["kolejka", "sledzenie", "kalendarz"]
    assert rows["B"]["page_views"] == 0 and rows["B"]["duration_min"] is None and rows["B"]["top_sections"] == []
    csv_body = client.get("/api/admin/demo-visitors.csv", headers=admin_headers).text
    assert "ekrany,czas_min,najczesciej" in csv_body
    assert ',7,12,"kolejka, sledzenie, kalendarz"' in csv_body


def test_view_is_rate_limited(client, gate, monkeypatch):
    monkeypatch.setattr(settings, "public_rate_limit_per_minute", 2)
    codes = [client.post(VIEW, json={"path": "/kolejka"}).status_code for _ in range(4)]
    assert codes[:2] == [204, 204] and 429 in codes[2:]


def test_same_session_counts_every_section(db_session, gate):
    """Kilka sygnałów w JEDNEJ sesji ORM (expire_on_commit=False) — sekcje nie mogą się gubić."""
    from app import demo_visitors

    visitor, token = demo_visitors.register(db_session, "Ewa", "Nowak", "Firma")
    for path in ("/kolejka", "/kolejka/1", "/"):
        visitor_activity.record_view(db_session, token, path)
    row = db_session.get(DemoVisitor, visitor.id, populate_existing=True)
    assert row.page_views == 3 and row.sections == {"kolejka": 2, "start": 1}
