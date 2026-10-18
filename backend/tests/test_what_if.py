"""US-062: symulacja „co jeśli statek się spóźni” — przesunięcie awizacji w zakresie użytkownika,
przeciążenie magazynu przed / po, nic nie zapisujemy."""
import datetime as dt

from sqlalchemy import func, select

from app import what_if
from app.database import SessionLocal
from app.models import Company, Container, ContainerStatus, Role, User, Warehouse, today_pl
from app.security import hash_password

from .conftest import login

S = ContainerStatus


def _setup(code):
    with SessionLocal() as db:
        mine, other = Company(name=f"WI {code}", code=code), Company(name=f"WI {code}X", code=f"{code}X")
        db.add_all([mine, other])
        db.flush()
        wh = Warehouse(name=f"Magazyn {code}", company_id=mine.id, default_daily_limit=2)
        db.add(wh)
        db.flush()
        db.add(User(login=f"logi-{code.lower()}", hashed_password=hash_password("pass12345"),
                    role=Role.logistics, company_id=mine.id))
        today = today_pl()
        d3, d8 = today + dt.timedelta(days=3), today + dt.timedelta(days=8)
        rows = [  # dzień +3: 3 kontenery (przeciążenie), dzień +8: 2 kontenery (limit)
            (mine.id, f"{code}U1000001", "MSC ALFA", d3), (mine.id, f"{code}U1000002", "MSC ALFA", d3),
            (other.id, f"{code}U1000003", "MSC ALFA", d3),
            (mine.id, f"{code}U1000004", "MSC BETA", d8), (mine.id, f"{code}U1000005", "MSC BETA", d8),
        ]
        for company_id, no, vessel, day in rows:
            db.add(Container(container_no=no, company_id=company_id, status=S.W_TRANSPORCIE, vessel=vessel,
                             warehouse_id=wh.id, notify_date=day))
        db.commit()
        return wh.id


def test_delay_moves_only_scoped_and_shows_overload(client):
    _setup("WIA")
    with SessionLocal() as db:
        user = db.scalars(select(User).where(User.login == "logi-wia")).one()
        before = db.scalar(select(func.count()).select_from(Container).where(Container.vessel == "MSC ALFA"))
        result = what_if.simulate(db, user, "MSC ALFA", 5)
        assert "MSC ALFA" in what_if.vessels(db, user)
        # nic nie zapisane
        assert db.scalar(select(func.count()).select_from(Container)
                         .where(Container.vessel == "MSC ALFA")) == before
        dates = {c.notify_date for c in db.scalars(select(Container).where(Container.vessel == "MSC ALFA"))}
    today = today_pl()
    assert dates == {today + dt.timedelta(days=3)}
    nos = {c["container_no"] for c in result["containers"]}
    assert nos == {"WIAU1000001", "WIAU1000002"}           # kontener innej spółki nie jest pokazany
    days = {d["day"]: d for d in result["days"]}
    d3, d8 = (today + dt.timedelta(days=n) for n in (3, 8))
    assert days[d3.isoformat()]["before"] == 3 and days[d3.isoformat()]["after"] == 1
    assert days[d8.isoformat()]["after"] == 4 and days[d8.isoformat()]["over_after"]
    assert result["resolved_overloads"] == 1 and result["new_overloads"] == 1


def test_endpoint_vessels_and_validation(client):
    _setup("WIB")
    headers = login(client, "logi-wib", "pass12345")
    r = client.get("/api/automations/what-if", headers=headers)
    assert r.status_code == 200
    assert {"MSC ALFA", "MSC BETA"} <= set(r.json()["vessels"])
    r = client.get("/api/automations/what-if", params={"vessel": "MSC BETA", "delay": 2}, headers=headers)
    assert r.status_code == 200 and len(r.json()["containers"]) == 2
    r = client.get("/api/automations/what-if", params={"vessel": "MSC BETA", "delay": 22}, headers=headers)
    assert r.status_code == 422
