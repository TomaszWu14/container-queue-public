"""US-040: „Symuluj dzień” — kroki obiegu automatów na danych demo, bez zapisu do bazy;
konto demo zostaje tylko do odczytu, a dane innych spółek nie wchodzą do symulacji."""
from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import AuditLog, JobRun, Notification
from tests.test_seed_demo_process import seeded  # noqa: F401 — fixture

from .conftest import login

PW = "Demo-Portfolio-2026"


def _counts():
    with SessionLocal() as db:
        return tuple(db.scalar(select(func.count()).select_from(m)) for m in (AuditLog, JobRun, Notification))


def test_simulation_walks_the_flow_without_writing(seeded, client):  # noqa: F811
    h = login(client, "demo", PW)
    before = _counts()
    r = client.get("/api/automations/simulate-day", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["available"] is True
    assert body["mail"]["found"] == [body["container_no"]]          # numer odczytany z treści maila
    inv = body["invoice"]
    assert inv and inv["lines"] == inv["rules"] + inv["ml"] + inv["user"] + inv["open"] > 0
    assert len(body["rules"]) == 3 and all(x["count"] >= 0 for x in body["rules"])
    assert body["event"]["signature"].startswith("sha256=") and body["event"]["bytes"] > 50
    assert body["total_minutes"] == sum(body["minutes"].values()) > 0
    assert _counts() == before                                       # nic nie zapisano
    assert client.post("/api/automations/test-event", headers=h).status_code == 403   # demo dalej tylko czyta


def test_no_containers_means_unavailable(client, admin_headers):
    from app.models import Company, Role, User
    from app.security import hash_password
    with SessionLocal() as db:
        co = Company(name="Sym pusta", code="SYM0")
        db.add(co)
        db.flush()
        db.add(User(login="sym-empty", hashed_password=hash_password("pass12345"), role=Role.logistics,
                    company_id=co.id))
        db.commit()
    body = client.get("/api/automations/simulate-day", headers=login(client, "sym-empty", "pass12345")).json()
    assert body == {"available": False}
