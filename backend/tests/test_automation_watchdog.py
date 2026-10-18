"""Druga lista PO, pkt 7: strażnik automatów — automat z harmonogramu bez udanego przebiegu dłużej niż
interwał + zapas zapala dzwonek adminów, raz dziennie na automat; automaty w normie nie hałasują."""
import datetime as dt

from app import automation_watchdog as W
from app.database import SessionLocal
from app.models import JobRun, Notification, utcnow


def _run(job, fn, hours_ago, ok=True):
    with SessionLocal() as db:
        db.add(JobRun(job=job, fn=fn, started_at=utcnow() - dt.timedelta(hours=hours_ago),
                      duration_ms=10, ok=ok, detail="0"))
        db.commit()


def _late_titles():
    with SessionLocal() as db:
        return [n.title for n in db.query(Notification).filter_by(kind=W.NOTIFY_KIND)]


def test_late_automation_rings_admins_once_a_day(client, admin_headers):
    _run("demurrage", "check_demurrage_alerts", hours_ago=30)          # interwał 6 h + 1 h zapasu → spóźniony
    _run("automation_rules", "run_rules", hours_ago=0.2)               # w normie
    with SessionLocal() as db:
        assert W.check_late_automations(db) >= 1
    titles = _late_titles()
    assert "Automat się spóźnia: demurrage" in titles
    assert "Automat się spóźnia: custom_rules" not in titles
    with SessionLocal() as db:
        again = W.check_late_automations(db)
    assert _late_titles().count("Automat się spóźnia: demurrage") == 1   # drugi raz tego dnia — cisza
    assert again == 0
    bell = client.get("/api/notifications", headers=admin_headers).json()
    items = bell["items"] if isinstance(bell, dict) else bell
    assert any(n["title"] == "Automat się spóźnia: demurrage" and "Ostatni udany przebieg" in n["body"]
               for n in items)


def test_watchdog_is_in_the_catalog(client, admin_headers):
    keys = {i["key"] for i in client.get("/api/automations", headers=admin_headers).json()["items"]}
    assert "watchdog" in keys
