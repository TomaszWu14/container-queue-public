"""Pulpit analityczny (prośba PO, widok w stylu Power BI): przepływ przez etapy, podziały wg
transportu, portu i odprawy oraz rozładunki tydzień po tygodniu — liczone w zakresie użytkownika."""
import datetime as dt

from sqlalchemy import text

from app.database import SessionLocal
from app.models import Container, TransportType
from app.models.enums import ContainerStatus as S
from app.models.enums import CustomsStatus as C
from app.routers.stats_overview import WEEKS_AHEAD, WEEKS_BACK
from tests.test_seed_demo_process import seeded  # noqa: F401 — fixture

from tests.test_forwarder_no_customs import _setup as forwarder_login

from .conftest import login


def _add(**kw):
    with SessionLocal() as db:
        company_id = db.execute(text("select id from companies limit 1")).scalar()
        for i, fields in enumerate(kw["rows"]):
            db.add(Container(container_no=f"TSTU{2000000 + i}", company_id=company_id, **fields))
        db.commit()


def test_counts_per_stage_mode_customs_and_week(client, admin_headers):
    today = dt.date.today()
    _add(rows=[
        {"status": S.W_TRANSPORCIE, "transport_type": TransportType.morski, "notify_date": today},
        {"status": S.W_PORCIE, "transport_type": TransportType.kolej, "customs_status": C.ZLECONA},
        {"status": S.W_PORCIE, "customs_status": C.ZWOLNIONY},
        {"status": S.ZREALIZOWANY, "transport_type": TransportType.morski},   # poza kolejką
    ])
    body = client.get(f"/api/stats/overview?today={today}", headers=admin_headers).json()
    stages = {s["status"]: s["count"] for s in body["stages"]}
    assert stages["W_TRANSPORCIE"] == 1 and stages["W_PORCIE"] == 2 and "ZREALIZOWANY" not in stages
    assert [s["status"] for s in body["stages"]][0] == "ZAPOWIEDZIANY"   # kolejność procesu
    assert {t["key"]: t["count"] for t in body["transport"]} == {"morski": 1, "kolej": 1, "lotniczy": 0,
                                                                  "inne": 1}
    assert body["customs"] == {"not_started": 1, "in_progress": 1, "cleared": 1}
    assert sum(p["count"] for p in body["ports"]) == 3
    weeks = body["weeks"]
    assert len(weeks) == WEEKS_BACK + WEEKS_AHEAD + 1
    current = [w for w in weeks if w["current"]]
    assert len(current) == 1 and current[0]["count"] == 1


def test_demo_data_fills_every_chart(seeded, client):  # noqa: F811
    body = client.get("/api/stats/overview", headers=login(client, "demo", "Demo-Portfolio-2026")).json()
    assert sum(s["count"] for s in body["stages"]) > 10
    assert len([p for p in body["ports"] if p["name"]]) >= 2
    assert sum(w["count"] for w in body["weeks"]) > 0


def test_forwarder_does_not_see_customs(client, admin_headers):
    hdr, _ = forwarder_login(client, admin_headers)
    body = client.get("/api/stats/overview", headers=hdr).json()
    assert body["customs"] is None
