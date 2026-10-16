"""Pomysł 2 PO: panel „Ile to oszczędza” liczy z danych aplikacji — zmiany zapisane w aplikacji
(z jawnym założeniem minut), dostawy na czas, komplet dokumentów u agencji, ostrzeżenia o karach."""
import datetime as dt

from app.database import SessionLocal
from app.models import AuditLog, Container, Notification, User
from app.models.enums import ContainerStatus as S
from app.routers.stats_value import MINUTES_PER_CHANGE
from tests.test_seed_demo_process import seeded  # noqa: F401 — fixture

from .conftest import login


def test_value_panel_counts_from_app_data(seeded, client):  # noqa: F811
    body = client.get("/api/stats/value", headers=login(client, "demo", "Demo-Portfolio-2026")).json()
    assert body["minutes_per_change"] == MINUTES_PER_CHANGE   # założenie widoczne na ekranie
    assert body["changes"] > 100
    assert body["hours_saved"] == round(body["changes"] * MINUTES_PER_CHANGE / 60, 1)
    assert 0 < body["delivered_on_time"] <= body["delivered"]
    assert 0 < body["docs_complete"] <= body["docs_in_flow"]


def test_on_time_and_demurrage_warnings(client, admin_headers):
    with SessionLocal() as db:
        admin = db.query(User).filter_by(login="admin").one()
        company_id = db.execute(__import__("sqlalchemy").text("select id from companies limit 1")).scalar()
        today = dt.date.today()
        late = Container(container_no="TSTU1000003", company_id=company_id, status=S.DOSTARCZONY,
                         notify_date=today - dt.timedelta(days=3))
        ok = Container(container_no="TSTU1000014", company_id=company_id, status=S.DOSTARCZONY,
                       notify_date=today)
        db.add_all([late, ok])
        db.flush()
        now = dt.datetime.now()
        for c in (late, ok):
            db.add(AuditLog(entity_type="containers", entity_id=c.id, field="status", old_value="W_DOSTAWIE",
                            new_value="DOSTARCZONY", user_id=admin.id, created_at=now))
        db.add(Notification(user_id=admin.id, kind="demurrage", title="kara", container_id=late.id))
        db.commit()
    body = client.get("/api/stats/value", headers=admin_headers).json()
    assert body["delivered"] == 2 and body["delivered_on_time"] == 1
    assert body["demurrage_warned"] == 1 and body["changes"] == 2
