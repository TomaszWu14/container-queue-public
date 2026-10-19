"""Przegląd dostępów (czwarta lista PO, pkt 9, US-076)."""
import datetime

from app import access_review
from app.database import SessionLocal
from app.models import Notification, Role, User, utcnow
from app.security import hash_password


def _add(db, login, role=Role.logistics, last_seen=None, view_all=True, totp=None, active=True):
    u = User(login=login, hashed_password=hash_password("x"), role=role, view_all_companies=view_all,  # gitleaks:allow
             last_seen=last_seen, totp_secret=totp, is_active=active)
    db.add(u)
    db.flush()
    return u


def test_review_lists_stale_never_admin_without_2fa_and_all_companies(client):
    now = utcnow()
    with SessionLocal() as db:
        _add(db, "aktywny", last_seen=now - datetime.timedelta(days=5), view_all=False)
        _add(db, "stary", last_seen=now - datetime.timedelta(days=120), view_all=False)
        _add(db, "nigdy", view_all=False)
        _add(db, "wylaczony", last_seen=None, active=False)
        _add(db, "wszystkie", last_seen=now, view_all=True)
        _add(db, "admin2", role=Role.admin, last_seen=now, totp="SECRET")
        r = access_review.review(db, now)
        db.rollback()
    stale = {x["login"]: x["reason"] for x in r["stale"]}
    assert stale["stary"] == "stale" and stale["nigdy"] == "never"
    assert "aktywny" not in stale and "wylaczony" not in stale
    assert "admin" in {x["login"] for x in r["admins_without_2fa"]}      # admin z conftest bez 2FA
    assert "admin2" not in {x["login"] for x in r["admins_without_2fa"]}
    assert "wszystkie" in {x["login"] for x in r["all_companies"]}


def test_endpoint_admin_only(client, admin_headers):
    r = client.get("/api/users/access-review", headers=admin_headers)
    assert r.status_code == 200, r.text
    assert r.json()["stale_days"] == 90


def test_quarter_day_window():
    # pierwszy poniedziałek kwietnia 2027 = 5.04; 8:00 PL (CEST) = 6:00 UTC
    assert access_review.is_review_day(datetime.datetime(2027, 4, 5, 6, 30))
    assert not access_review.is_review_day(datetime.datetime(2027, 4, 12, 6, 30))   # drugi poniedziałek
    assert not access_review.is_review_day(datetime.datetime(2027, 5, 3, 6, 30))    # nie kwartał
    assert not access_review.is_review_day(datetime.datetime(2027, 4, 5, 9, 30))    # po 8:00


def test_quarterly_reminder_goes_to_admins_once(client):
    when = datetime.datetime(2027, 4, 5, 6, 30)
    with SessionLocal() as db:
        assert access_review.check_access_review(db, when) >= 1
        assert access_review.check_access_review(db, when) == 0
        kinds = db.query(Notification).filter(Notification.kind == access_review.NOTIFY_KIND).all()
        assert kinds and all(db.get(User, n.user_id).role == Role.admin for n in kinds)
        assert access_review.check_access_review(db, datetime.datetime(2027, 4, 6, 6, 30)) == 0
