"""US-038: analiza przebiegu procesu z historii statusów — czas w etapach (mediana, 90. percentyl),
cofnięcia, najczęstsze przejścia i kontenery utknięte dłużej niż zwykle; zakres spółek."""
import datetime as dt

from app import process_mining
from app.database import SessionLocal
from app.models import AuditLog, Company, Container, ContainerStatus, Role, User, utcnow
from app.security import hash_password

from .conftest import login

S = ContainerStatus
NOW = utcnow()


def _company(code):
    with SessionLocal() as db:
        c = Company(name=f"Proc {code}", code=code)
        db.add(c)
        db.commit()
        return c.id


def _user(login_, company_id):
    with SessionLocal() as db:
        db.add(User(login=login_, hashed_password=hash_password("pass12345"), role=Role.logistics,
                    company_id=company_id))
        db.commit()


def _container(company_id, no, created_days_ago, steps, status):
    """steps: [(dni temu, stary status, nowy status)] — wpisy dziennika zmian statusu."""
    with SessionLocal() as db:
        c = Container(container_no=no, company_id=company_id, status=status,
                      created_at=NOW - dt.timedelta(days=created_days_ago))
        db.add(c)
        db.flush()
        for ago, old, new in steps:
            db.add(AuditLog(entity_type="containers", entity_id=c.id, field="status",
                            old_value=old.value, new_value=new.value,
                            created_at=NOW - dt.timedelta(days=ago)))
        db.commit()


def test_percentile_linear():
    assert process_mining._percentile([1.0], 0.9) == 1.0
    assert process_mining._percentile([1.0, 2.0, 3.0, 4.0, 5.0], 0.5) == 3.0
    assert round(process_mining._percentile([1.0, 2.0, 3.0, 4.0, 5.0], 0.9), 2) == 4.6


def test_stage_times_backward_and_stuck(client):
    cid = _company("PRM1")
    _user("logi-prm1", cid)
    # 5 kontenerów: port 2, 3, 4, 5, 6 dni → mediana 4, p90 5,6
    for i, port_days in enumerate((2, 3, 4, 5, 6)):
        _container(cid, f"PRMU100000{i}", 40, [
            (30, S.W_TRANSPORCIE, S.W_PORCIE),
            (30 - port_days, S.W_PORCIE, S.ODPRAWA),
        ], S.ODPRAWA)
    # cofnięcie: odprawa → port (poprawka), potem znów odprawa
    _container(cid, "PRMU2000001", 20, [
        (10, S.W_PORCIE, S.ODPRAWA), (9, S.ODPRAWA, S.W_PORCIE), (8, S.W_PORCIE, S.ODPRAWA)], S.ODPRAWA)
    # utknięty: w porcie od 12 dni (p90 portu ~5,6) / świeży: w porcie od 1 dnia
    _container(cid, "PRMU3000001", 20, [(12, S.W_TRANSPORCIE, S.W_PORCIE)], S.W_PORCIE)
    _container(cid, "PRMU3000002", 20, [(1, S.W_TRANSPORCIE, S.W_PORCIE)], S.W_PORCIE)

    body = client.get("/api/automations/process", headers=login(client, "logi-prm1", "pass12345")).json()
    port = next(s for s in body["stages"] if s["status"] == "W_PORCIE")
    assert port["count"] == 7          # 5 pobytów + 2 z kontenera z cofnięciem (10 dni, 1 dzień)
    assert port["median_days"] == 4.0 and port["p90_days"] == 7.6
    assert body["backward"] == 1 and body["transitions_total"] == 15
    assert {"from": "W_PORCIE", "to": "ODPRAWA", "count": 7} in body["top_transitions"]
    assert {"from": "ODPRAWA", "to": "W_PORCIE", "count": 1} in body["transitions"]          # cofnięcie też
    assert sum(t["count"] for t in body["transitions"]) == body["transitions_total"]
    assert [s["container_no"] for s in body["stuck"]] == ["PRMU3000001"]
    assert body["stuck"][0]["days_in_stage"] == 12.0
    assert all(s["status"] != "ZREALIZOWANY" for s in body["stages"])


def test_scoped_and_window(client, admin_headers):
    a, b = _company("PRM2"), _company("PRM3")
    _user("logi-prm2", a)
    _container(a, "PRMU4000001", 10, [(5, S.W_PORCIE, S.ODPRAWA)], S.ODPRAWA)
    _container(b, "PRMU4000002", 10, [(5, S.W_PORCIE, S.ODPRAWA)], S.ODPRAWA)
    _container(a, "PRMU4000003", 300, [(200, S.W_PORCIE, S.ODPRAWA)], S.ODPRAWA)   # poza oknem 90 dni
    mine = client.get("/api/automations/process", headers=login(client, "logi-prm2", "pass12345")).json()
    assert mine["transitions_total"] == 1 and mine["stuck"] == []
    wide = client.get("/api/automations/process?days=365",
                      headers=login(client, "logi-prm2", "pass12345")).json()
    assert wide["transitions_total"] == 2
    assert client.get("/api/automations/process?days=5", headers=admin_headers).status_code == 422


def test_empty_is_not_an_error(client):
    cid = _company("PRM4")
    _user("logi-prm4", cid)
    body = client.get("/api/automations/process", headers=login(client, "logi-prm4", "pass12345")).json()
    assert body["transitions_total"] == 0 and body["backward_pct"] is None and body["stuck_total"] == 0
    assert all(s["median_days"] is None for s in body["stages"])


def test_delivered_containers_are_not_stuck(client):
    """Po dostawie na magazyn czekanie na rozliczenie nie trafia na listę „do sprawdzenia” (Z-027)."""
    cid = _company("PRM5")
    _user("logi-prm5", cid)
    for i, days in enumerate((1, 2, 2, 3, 3)):      # p90 etapu DOSTARCZONY ≈ 3 dni
        _container(cid, f"PRMU500000{i}", 30, [(20, S.W_DOSTAWIE, S.DOSTARCZONY),
                                               (20 - days, S.DOSTARCZONY, S.ZREALIZOWANY)], S.ZREALIZOWANY)
    _container(cid, "PRMU5000009", 30, [(25, S.W_DOSTAWIE, S.DOSTARCZONY)], S.DOSTARCZONY)   # 25 dni po dostawie
    body = client.get("/api/automations/process", headers=login(client, "logi-prm5", "pass12345")).json()
    assert next(s for s in body["stages"] if s["status"] == "DOSTARCZONY")["count"] == 5
    assert body["stuck"] == [] and body["stuck_total"] == 0
