"""Karta spedytora (czwarta lista PO, pkt 5, US-079)."""
import datetime

from app import forwarder_scorecard as fs
from app.database import SessionLocal
from app.models import AvizoRequest, Company, Container, DeliveryConfirmation, Forwarder, User, utcnow


def _req(db, co, fw, n, sent_ago_h, answer_after_h=None, decisions=(), rejected=""):
    req = AvizoRequest(token=f"fs-{fw.id}-{n}", company_id=co.id, forwarder_id=fw.id,
                       created_at=utcnow() - datetime.timedelta(hours=sent_ago_h), reject_comment=rejected)
    db.add(req)
    db.flush()
    for i, d in enumerate(decisions):
        c = Container(container_no=f"FSC{fw.id}{n}{i}", company_id=co.id)
        db.add(c)
        db.flush()
        db.add(DeliveryConfirmation(request_id=req.id, container_id=c.id, decision=d,
                                    submitted_at=req.created_at + datetime.timedelta(hours=answer_after_h)))
    return req


def test_scorecard_ranks_by_on_time_answers(client):
    with SessionLocal() as db:
        co = db.query(Company).first()
        fast, slow = Forwarder(name="Szybka Spedycja"), Forwarder(name="Wolna Spedycja")
        db.add_all([fast, slow])
        db.flush()
        _req(db, co, fast, 1, 100, 2, ("confirmed", "confirmed"))
        _req(db, co, fast, 2, 100, 6, ("date_change",))
        _req(db, co, slow, 1, 200, 50, ("problem", "confirmed"))
        _req(db, co, slow, 2, 10)                                     # bez odpowiedzi
        _req(db, co, slow, 3, 24 * 200, 1, ("confirmed",))             # poza oknem 90 dni
        _req(db, co, slow, 4, 30, 5, ("confirmed",), rejected="zły slot")
        admin = db.query(User).filter_by(login="admin").one()
        db.flush()
        rows = {r["forwarder"]: r for r in fs.scorecard(db, admin)["forwarders"]}
        order = [r["forwarder"] for r in fs.scorecard(db, admin)["forwarders"]]
        db.rollback()
    f, s = rows["Szybka Spedycja"], rows["Wolna Spedycja"]

    assert (f["requests"], f["answered"], f["median_hours"], f["on_time_pct"]) == (2, 2, 4.0, 100.0)
    assert f["date_change_pct"] == round(100 / 3, 1) and f["problem_pct"] == 0.0
    assert (s["requests"], s["answered"], s["rejected"]) == (3, 2, 1)
    assert s["on_time_pct"] == round(100 / 3, 1) and s["problem_pct"] == round(100 / 3, 1)
    assert order.index("Szybka Spedycja") < order.index("Wolna Spedycja")


def test_endpoint_for_editors(client, admin_headers):
    r = client.get("/api/automations/forwarder-scorecard", headers=admin_headers)
    assert r.status_code == 200, r.text
    assert r.json()["on_time_hours"] == 24
