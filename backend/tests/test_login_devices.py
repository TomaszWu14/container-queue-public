"""Mail „logowanie z nowego urządzenia” (czwarta lista PO, pkt 8, US-075)."""
import pytest

from app import login_devices
from app.database import SessionLocal
from app.models import AppSetting

CHROME_WIN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"
FIREFOX_LINUX = "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0"


@pytest.fixture()
def sent(monkeypatch):
    mails: list[tuple[list[str], str, str]] = []
    from app import notifications
    monkeypatch.setattr(notifications, "send_html_email",
                        lambda to, subject, html, **kw: mails.append((to, subject, html)))
    return mails


def _user(client, admin_headers, email="anna@example.com"):
    r = client.post("/api/users", headers=admin_headers, json={
        "login": "anna.dev", "password": "haslo1234567", "role": "logistics", "email": email,
        "full_name": "Anna Nowak", "view_all_companies": True})
    assert r.status_code == 201, r.text


def _login(client, ua):
    r = client.post("/api/auth/login", data={"username": "anna.dev", "password": "haslo1234567"},
                    headers={"User-Agent": ua})
    assert r.status_code == 200, r.text


def test_first_login_remembers_device_without_mail(client, admin_headers, sent):
    _user(client, admin_headers)
    _login(client, CHROME_WIN)
    assert sent == []


def test_new_browser_sends_mail_known_one_does_not(client, admin_headers, sent):
    _user(client, admin_headers)
    _login(client, CHROME_WIN)
    _login(client, CHROME_WIN)
    assert sent == []
    _login(client, FIREFOX_LINUX)
    assert len(sent) == 1
    to, subject, html = sent[0]
    assert to == ["anna@example.com"]
    assert "Nowe logowanie" in subject
    assert "Firefox · Linux" in html and "Anna Nowak" in html
    _login(client, FIREFOX_LINUX)
    assert len(sent) == 1


def test_user_agent_stored_only_as_hash(client, admin_headers, sent):
    _user(client, admin_headers)
    _login(client, CHROME_WIN)
    with SessionLocal() as db:
        values = [s.value for s in db.query(AppSetting).filter(AppSetting.key.like("known_devices:%"))]
    assert values and all("Chrome" not in v and "Windows" not in v for v in values)


def test_no_email_no_mail_and_mail_failure_does_not_block_login(client, admin_headers, monkeypatch):
    _user(client, admin_headers)
    _login(client, CHROME_WIN)
    from app import notifications

    def boom(*a, **k):
        raise RuntimeError("SMTP nieskonfigurowany")
    monkeypatch.setattr(notifications, "send_html_email", boom)
    _login(client, FIREFOX_LINUX)   # wyjątek wysyłki nie psuje logowania


def test_device_list_is_capped():
    class U:
        id, login, email = 999, "x", ""
    with SessionLocal() as db:
        for i in range(login_devices.MAX_DEVICES + 5):
            login_devices.remember(db, U(), f"agent-{i}")  # type: ignore[arg-type]
        assert len(login_devices._load(db, 999)) == login_devices.MAX_DEVICES
        db.rollback()


@pytest.mark.parametrize("ua, expected", [
    (CHROME_WIN, "Chrome · Windows"),
    ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) Safari/604.1", "Safari · iOS"),
    ("Mozilla/5.0 (Windows NT 10.0) Chrome/130.0 Safari/537.36 Edg/130.0", "Edge · Windows"),
    ("", "nieznana przeglądarka · nieznany system"),
])
def test_describe(ua, expected):
    assert login_devices.describe(ua) == expected
