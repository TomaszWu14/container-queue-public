"""Trzecia lista PO, pkt 3: osobiste wyciszenie alertów kontenera na 1 / 3 / 7 dni; wzmianki przechodzą,
inni odbiorcy dostają alert; kontener spoza zakresu → 404; po terminie wyciszenie wygasa."""
import datetime as dt

from app import alert_mutes
from app.database import SessionLocal
from app.models import Company, Container, Notification, Role, User, today_pl
from app.notifications import notify
from app.security import hash_password

from .conftest import login


def _setup():
    with SessionLocal() as db:
        a, b = Company(name="Mute A", code="MUTA"), Company(name="Mute B", code="MUTB")
        db.add_all([a, b])
        db.flush()
        for name, comp in (("logi-mute1", a), ("logi-mute2", a)):
            db.add(User(login=name, hashed_password=hash_password("pass12345"), role=Role.logistics,
                        company_id=comp.id))
        mine = Container(container_no="MUTU1000001", company_id=a.id)
        other = Container(container_no="MUTU1000002", company_id=b.id)
        db.add_all([mine, other])
        db.commit()
        return mine.id, other.id


def test_mute_skips_only_that_user_and_container(client):
    mine, other = _setup()
    h = login(client, "logi-mute1", "pass12345")
    r = client.post("/api/notifications/mutes", headers=h, json={"container_id": mine, "days": 3})
    assert r.status_code == 200, r.text
    assert r.json()["until"] == (today_pl() + dt.timedelta(days=3)).isoformat()
    assert client.post("/api/notifications/mutes", headers=h, json={"container_id": other, "days": 3}).status_code == 404
    assert client.post("/api/notifications/mutes", headers=h, json={"container_id": mine, "days": 2}).status_code == 422
    assert [m["container_no"] for m in client.get("/api/notifications/mutes", headers=h).json()] == ["MUTU1000001"]

    with SessionLocal() as db:
        u1 = db.query(User).filter_by(login="logi-mute1").one()
        u2 = db.query(User).filter_by(login="logi-mute2").one()
        assert notify(db, [u1, u2], kind="rule", title="Alert", container_id=mine) == 1
        assert notify(db, [u1], kind="mention", title="@ty", container_id=mine, ignore_watch_only=True) == 1
        db.commit()
        got = {(n.user_id, n.title) for n in db.query(Notification).filter_by(container_id=mine)}
        assert got == {(u2.id, "Alert"), (u1.id, "@ty")}
        # po terminie wyciszenie wygasa
        later = today_pl() + dt.timedelta(days=4)
        assert alert_mutes.muted_users(db, [u1.id], mine, today=later) == set()

    assert client.delete(f"/api/notifications/mutes/{mine}", headers=h).status_code == 200
    assert client.get("/api/notifications/mutes", headers=h).json() == []
