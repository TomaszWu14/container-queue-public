"""Trzecia lista PO, pkt 2: test reguły na ostatnich 30 dniach — etap z historii statusów, jeden alert na
kontener i dzień, tylko kontenery w zakresie użytkownika, nic nie zapisujemy."""
import datetime as dt

from app import automation_rules as R
from app import automation_rules_backtest as B
from app.database import SessionLocal
from app.models import AuditLog, Company, Container, Notification, Role, User
from app.models.enums import ContainerStatus as S
from app.security import hash_password

from .conftest import login

TODAY = dt.date(2026, 10, 19)


def _mk(db, company, no, status, created_days_ago, **kw):
    c = Container(container_no=no, company_id=company.id, status=status,
                  created_at=dt.datetime.combine(TODAY - dt.timedelta(days=created_days_ago), dt.time(8)), **kw)
    db.add(c)
    db.flush()
    return c


def test_eta_passed_counts_one_alert_per_open_day():
    with SessionLocal() as db:
        comp = Company(name="BT A", code="BTA")
        db.add(comp)
        db.flush()
        # ETA 10 dni temu, dostarczony 4 dni temu → reguła „ETA minęło ≥3 dni” trafia od dnia −7 do −5
        c = _mk(db, comp, "BTAU1000001", S.DOSTARCZONY, 40, eta=TODAY - dt.timedelta(days=10))
        db.add(AuditLog(entity_type="containers", entity_id=c.id, field="status", old_value=S.W_PORCIE.value,
                        new_value=S.DOSTARCZONY.value,
                        created_at=dt.datetime.combine(TODAY - dt.timedelta(days=4), dt.time(9))))
        db.commit()
        rule = R.Rule.model_validate({"name": "t", "condition": "eta_passed", "days": 3})
        out = B.backtest(db, rule, scope=lambda q: q.where(Container.company_id == comp.id), today=TODAY)
        hits = [d["day"] for d in out["per_day"] if d["alerts"]]
        assert hits == [(TODAY - dt.timedelta(days=k)).isoformat() for k in (7, 6, 5)]
        assert out["alerts"] == 3 and out["containers"] == 1 and out["max_per_day"] == 1


def test_endpoint_scoped_and_no_writes(client):
    with SessionLocal() as db:
        a, b = Company(name="BT B", code="BTB"), Company(name="BT C", code="BTC")
        db.add_all([a, b])
        db.flush()
        db.add(User(login="logi-bt", hashed_password=hash_password("pass12345"), role=Role.logistics, company_id=a.id))
        soon = dt.date.today() + dt.timedelta(days=1)
        _mk(db, a, "BTBU1000001", S.AWIZOWANY, 2, notify_date=soon)
        _mk(db, b, "BTCU1000001", S.AWIZOWANY, 2, notify_date=soon)
        db.commit()
        before = db.query(Notification).count()
    h = login(client, "logi-bt", "pass12345")
    r = client.get("/api/automations/rules/backtest", headers=h, params={"condition": "no_driver", "days": 2})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["days"] == 30 and body["containers"] == 1          # kontener innej spółki nie liczony
    assert body["per_day"][-1]["alerts"] == 1
    assert client.get("/api/automations/rules/backtest", headers=h,
                      params={"condition": "notify_soon_status", "days": 2}).status_code == 422
    with SessionLocal() as db:
        assert db.query(Notification).count() == before
