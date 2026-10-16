"""Pomysł 10 PO: ryzyko kary za przestój z wyjaśnieniem — dostawa zaplanowana po końcu wolnych dni
(ile dni kary), brak terminu dostawy tuż przed końcem wolnych dni; bezpieczne i zakończone pominięte."""
import datetime as dt

from sqlalchemy import text

from app.database import SessionLocal
from app.models import Container
from app.models.enums import ContainerStatus as S
from app.models.enums import today_pl


def _add(db, no, eta, free_days, planned=None, status=S.W_PORCIE):
    company_id = db.execute(text("select id from companies limit 1")).scalar()
    c = Container(container_no=no, company_id=company_id, status=status, eta=eta,
                  demurrage_free_days=free_days, notify_date=planned)
    db.add(c)
    return c


def test_risks_explain_why_and_skip_safe(client, admin_headers):
    today = today_pl()
    with SessionLocal() as db:
        late = _add(db, "RSKU1000001", today - dt.timedelta(days=2), 5, planned=today + dt.timedelta(days=6))
        near = _add(db, "RSKU1000002", today - dt.timedelta(days=4), 6)
        _add(db, "RSKU1000003", today - dt.timedelta(days=1), 10, planned=today + dt.timedelta(days=2))
        _add(db, "RSKU1000004", today - dt.timedelta(days=9), 3, status=S.DOSTARCZONY)
        db.commit()
        late_id, near_id = late.id, near.id
    rows = client.get("/api/stats/demurrage-risk", headers=admin_headers).json()
    by_id = {r["container_id"]: r for r in rows}
    assert set(by_id) == {late_id, near_id}
    assert by_id[late_id]["reason"] == "planned_after_deadline" and by_id[late_id]["days_over"] == 3
    assert by_id[late_id]["deadline"] == (today + dt.timedelta(days=3)).isoformat()
    assert by_id[near_id]["reason"] == "unplanned_near_deadline" and by_id[near_id]["days_left"] == 2
    assert rows[0]["container_id"] == near_id   # najpilniejsze pierwsze

