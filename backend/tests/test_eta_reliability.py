"""Trzecia lista PO, pkt 7: punktualność armatora i portu z historii (pierwsze ETA vs faktyczny wyładunek)
i „realne ETA” dla kontenerów w drodze; tylko zakres użytkownika, bez zapisu."""
import datetime as dt

from app import eta_reliability as E
from app.database import SessionLocal
from app.models import AuditLog, Carrier, Company, Container, Port, Role, TrackingEvent, User, today_pl
from app.models.enums import ContainerStatus as S
from app.security import hash_password

from .conftest import login


def _setup(code):
    today = today_pl()
    with SessionLocal() as db:
        a, b = Company(name=f"ETA {code}", code=code), Company(name=f"ETA {code}X", code=f"{code}X")
        car, port = Carrier(name=f"Armator {code}"), Port(name=f"PORT{code}")
        db.add_all([a, b, car, port])
        db.flush()
        db.add(User(login=f"logi-{code.lower()}", hashed_password=hash_password("pass12345"),
                    role=Role.logistics, company_id=a.id))
        for i, late in enumerate((2, 3, 4, 10)):          # mediana 3,5 → przesunięcie 4 dni
            planned = today - dt.timedelta(days=40 + i)
            c = Container(container_no=f"{code}U100000{i}", company_id=a.id, carrier_id=car.id, port_id=port.id,
                          status=S.DOSTARCZONY, eta=planned + dt.timedelta(days=late))
            db.add(c)
            db.flush()
            db.add(AuditLog(entity_type="containers", entity_id=c.id, field="eta", old_value=planned.isoformat(),
                            new_value=(planned + dt.timedelta(days=late)).isoformat()))
            db.add(TrackingEvent(container_id=c.id, event_code="DISCHARGE", description="x", is_estimated=False,
                                 occurred_at=dt.datetime.combine(planned + dt.timedelta(days=late), dt.time(10))))
        # obca spółka: ten sam armator, ogromne spóźnienie — nie może wpłynąć na wynik
        f = Container(container_no=f"{code}U2000000", company_id=b.id, carrier_id=car.id, port_id=port.id,
                      status=S.DOSTARCZONY, eta=today - dt.timedelta(days=30))
        db.add(f)
        db.flush()
        db.add(TrackingEvent(container_id=f.id, event_code="DISCHARGE", description="x", is_estimated=False,
                             occurred_at=dt.datetime.combine(today, dt.time(10))))
        db.add(Container(container_no=f"{code}U3000000", company_id=a.id, carrier_id=car.id, port_id=port.id,
                         status=S.W_TRANSPORCIE, eta=today + dt.timedelta(days=10)))
        db.commit()
        return car.name, today


def test_carrier_stats_and_realistic_eta(client):
    carrier, today = _setup("ETR")
    h = login(client, "logi-etr", "pass12345")
    r = client.get("/api/automations/eta-reliability", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    row = next(x for x in body["carriers"] if x["carrier"] == carrier)
    assert row["arrivals"] == 4 and row["median_days"] == 3.5 and row["late_pct"] == 100
    fc = next(x for x in body["forecasts"] if x["container_no"] == "ETRU3000000")
    assert fc["shift_days"] == 4 and fc["basis"] == "carrier_port"
    assert fc["realistic_eta"] == (today + dt.timedelta(days=14)).isoformat()


def test_too_few_arrivals_no_forecast():
    with SessionLocal() as db:
        out = E.analyze(db, db.query(User).filter_by(login="admin").one())
    assert out["min_arrivals"] == E.MIN_ARRIVALS
