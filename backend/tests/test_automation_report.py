"""Druga lista PO, pkt 9: tygodniowy raport automatów — w poniedziałek 8:00–9:00 (PL) admin i logistyka
dostają jedno powiadomienie z zaoszczędzonymi godzinami, przebiegami, automatami wymagającymi uwagi
i najlepszymi automatami; poza oknem i drugi raz tego samego dnia — nic."""
import datetime as dt

from app import automation_report as R
from app.database import SessionLocal
from app.models import JobRun, Notification, Role, User

# poniedziałek 2026-10-19, 8:30 czasu PL = 6:30 UTC (CEST)
MONDAY_830 = dt.datetime(2026, 10, 19, 6, 30)


def _reports():
    with SessionLocal() as db:
        return db.query(Notification).filter_by(kind=R.NOTIFY_KIND).all()


def test_monday_report_once_for_admin_and_logistics(client, admin_headers):
    with SessionLocal() as db:
        db.add(JobRun(job="demurrage", fn="check_demurrage_alerts", started_at=MONDAY_830 - dt.timedelta(hours=1),
                      duration_ms=5, ok=True, detail="12"))
        db.commit()
        assert R.check_automation_weekly_report(db, now=MONDAY_830 - dt.timedelta(hours=2)) == 0   # 6:30 PL — poza oknem
        sent = R.check_automation_weekly_report(db, now=MONDAY_830)
        roles = {db.get(User, n.user_id).role for n in _reports()}
    assert sent >= 1 and roles <= {Role.admin, Role.logistics} and Role.admin in roles
    report = next(n for n in _reports() if "demurrage" in n.body)
    assert report.title.startswith("Automaty w tym tygodniu: ok.")
    assert "Zaoszczędzone" in report.body and "Najwięcej oszczędziły: demurrage (1.0 h)" in report.body
    with SessionLocal() as db:   # powiadomienia mają czas zegara; test udaje poniedziałek — wyrównujemy
        for n in db.query(Notification).filter_by(kind=R.NOTIFY_KIND):
            n.created_at = MONDAY_830
        db.commit()
        assert R.check_automation_weekly_report(db, now=MONDAY_830 + dt.timedelta(minutes=20)) == 0


def test_body_lists_attention_or_none():
    cat = {"summary": {"hours_saved": 0, "runs": 0, "effects": 0, "active": 1, "total": 2},
           "items": [{"key": "tracking", "status": "late", "minutes_saved": 0}]}
    assert "Wymagają uwagi: tracking (late)" in R.body(cat)
    cat["items"][0]["status"] = "ok"
    assert "Wymagają uwagi: brak." in R.body(cat)
