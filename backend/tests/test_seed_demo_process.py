"""US-027 / US-028: demo pokazuje cały proces (odprawa, demurrage, zamówienia, dokumenty,
awizacje), a konta demo per rola widzą tylko swoje i niczego nie zapiszą.
Kryteria akceptacji: docs/analiza/HISTORYJKI.md."""
import datetime as dt

import pytest

from app.config import settings
from app.database import SessionLocal
from app.document_tiles import required
from app.models import (Attachment, AvizoRequest, AvizoStatus, Container, CustomsStatus,
                        DeliveryConfirmation, Order, Role, User, customs_rank)
from app.models.enums import ContainerStatus as S
from app.models.enums import today_pl
from app.notification_alerts import demurrage_deadlines
from scripts import seed_demo

from .conftest import login

PW = "Demo-Portfolio-2026"
LOGINS = ["demo", "demo-spedytor", "demo-agencja", "demo-magazyn"]


@pytest.fixture()
def seeded(client, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "demo_readonly_logins", ",".join(LOGINS))
    monkeypatch.setattr(settings, "uploads_dir", str(tmp_path))
    seed_demo.wipe()
    assert seed_demo.seed(LOGINS, PW) == 150
    return tmp_path


def test_customs_matches_container_stage(seeded):
    with SessionLocal() as db:
        cs = db.query(Container).all()
        early = (S.ZAPOWIEDZIANY, S.W_PRODUKCJI, S.TRANSPORT_WSTEPNY)
        assert all(c.customs_status == CustomsStatus.BRAK for c in cs if c.status in early)
        assert all(c.customs_status != CustomsStatus.BRAK for c in cs if c.status == S.ODPRAWA)
        assert all(c.customs_status == CustomsStatus.ROZLICZONY for c in cs if c.status == S.ZREALIZOWANY)
        rewizja = [c for c in cs if c.customs_status == CustomsStatus.REWIZJA]
        assert rewizja and all(c.customs_note and c.customs_date for c in rewizja)
        # agencja przypisana dokładnie wtedy, gdy odprawę jej zlecono
        zlecona = customs_rank(CustomsStatus.ZLECONA)
        assert all((c.customs_agency_id is not None) == (customs_rank(c.customs_status) >= zlecona)
                   for c in cs)
        assert all(c.notify_date for c in cs if c.status in (S.AWIZOWANY, S.W_DOSTAWIE))


def test_demurrage_alerts_orders_and_ports(seeded):
    today = today_pl()
    with SessionLocal() as db:
        cs = db.query(Container).all()
        assert all(c.carrier_id and c.port_id for c in cs)
        deadlines = demurrage_deadlines(db, cs)
        soon = [cid for cid, d in deadlines.items() if d and 0 <= (d - today).days <= 3]
        assert len(soon) >= 3   # alert demurrage (FR-028) ma kogo pokazać
        orders = db.query(Order).all()
        assert len(orders) == 30 and all(len(o.containers) == o.container_count == 3 for o in orders)


def test_documents_have_files_and_deliberate_gaps(seeded):
    with SessionLocal() as db:
        cs = db.query(Container).all()
        by_container: dict[int, set[str]] = {}
        for a in db.query(Attachment).all():
            assert (seeded / a.stored_name).is_file() and a.size > 0
            if a.document_type.tile_code:
                by_container.setdefault(a.container_id, set()).add(a.document_type.tile_code)
        complete = [c for c in cs if required(c) and required(c) <= by_container.get(c.id, set())]
        missing = [c for c in cs if required(c) - by_container.get(c.id, set())]
        assert len(complete) > 50 and 5 <= len(missing) < 40


def test_avizo_requests_cover_the_workflow(seeded):
    with SessionLocal() as db:
        states = {r.status for r in db.query(AvizoRequest).all()}
        assert {AvizoStatus.SENT_STAGE1, AvizoStatus.CONFIRMED_BY_FORWARDER,
                AvizoStatus.REJECTED, AvizoStatus.CLOSED} <= states
        assert db.query(DeliveryConfirmation).filter_by(decision="date_change").count() >= 1
        rejected = db.query(AvizoRequest).filter_by(status=AvizoStatus.REJECTED).one()
        assert rejected.reject_comment


@pytest.mark.parametrize("login_name, role", [("demo", Role.logistics), ("demo-spedytor", Role.forwarder),
                                              ("demo-agencja", Role.customs),
                                              ("demo-magazyn", Role.warehouse)])
def test_role_accounts_see_own_scope_and_cannot_write(seeded, client, login_name, role):
    with SessionLocal() as db:
        user = db.query(User).filter_by(login=login_name).one()
        assert user.role == role
        everything = db.query(Container).count()
    hdr = login(client, login_name, PW)
    rows = client.get("/api/containers?limit=500", headers=hdr).json()
    assert rows   # każda rola ma co oglądać
    if role != Role.logistics:
        assert len(rows) < everything   # partner i magazyn widzą tylko swoje
    with SessionLocal() as db:
        if role == Role.forwarder:
            assert {db.get(Container, r["id"]).forwarder_id for r in rows} == {user.forwarder_id}
        if role == Role.customs:
            assert {db.get(Container, r["id"]).customs_agency_id for r in rows} == {user.customs_agency_id}
        if role == Role.warehouse:
            assert {db.get(Container, r["id"]).warehouse_id for r in rows} == {user.warehouse_id}
    write = client.patch(f"/api/containers/{rows[0]['id']}", headers=hdr, json={"notes": "x"})
    assert write.status_code == 403 and "demo" in write.json()["detail"].lower()


def test_seed_is_deterministic_in_dates(seeded):
    with SessionLocal() as db:
        assert all(c.etd < c.eta for c in db.query(Container).all() if c.etd)
        assert all(r.expires_at > dt.datetime.now() - dt.timedelta(minutes=1)
                   for r in db.query(AvizoRequest).all())


def test_forwarder_scorecard_has_demo_history(seeded):
    """US-079: karta spedytora w demo — trzy spedycje z różnym czasem odpowiedzi, ranking od najszybszej."""
    from app.forwarder_scorecard import scorecard
    from app.models import Role, User
    with SessionLocal() as db:
        admin = db.query(User).filter_by(role=Role.admin).first()
        rows = scorecard(db, admin)["forwarders"]
    assert len(rows) >= 3 and all(r["answered"] for r in rows)
    assert rows[0]["forwarder"] == "Spedycja Demo" and rows[-1]["on_time_pct"] < rows[0]["on_time_pct"]


def test_demo_map_has_moving_vessels(seeded, client):
    # mapa śledzenia w demo nie jest pusta: statki z kolejki mają pozycję, trasę i port docelowy
    hdr = login(client, "demo", PW)
    vessels = client.get("/api/tracking/vessels", headers=hdr).json()
    assert len(vessels) == 4
    assert all(v["lat"] is not None and len(v["trail"]) >= 2 and v["destination"] for v in vessels)
    assert sum(1 for v in vessels if v["near_port"]) == 1   # jeden czeka na redzie
    assert all(v["containers"] > 0 for v in vessels)
