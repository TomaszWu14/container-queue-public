"""US-017 (P-09): „Wyślij plan” wysyła spedytorowi maila z proponowanymi datami i linkiem do
zakładki Spedycja; jeden mail na spedytora i spółkę; brak adresu albo poczty = jawna informacja,
a status planu i tak jest zapisany (spedytor z kontem widzi plan w aplikacji)."""
import pytest

from app import plan_mail
from app.config import settings
from app.iso6346 import check_digit
from app.models import AuditLog, Container, Forwarder, PlanningStatus
from tests.conftest import login
from tests.test_planning_confirm import _create, _d, _forwarder_id


def _no(serial: str) -> str:
    return f"PLNU{serial}{check_digit('PLNU' + serial)}"


@pytest.fixture
def sent_mails(monkeypatch):
    mails = []
    monkeypatch.setattr(plan_mail, "send_html_email",
                        lambda to, subject, html, reply_to="": mails.append((to, subject, html)))
    monkeypatch.setattr(settings, "public_base_url", "https://kolejka.example")
    return mails


def _send(client, headers, ids):
    resp = client.post("/api/containers/plan/send", json={"container_ids": ids}, headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _set_email(db_session, forwarder_id, email):
    db_session.get(Forwarder, forwarder_id).email = email
    db_session.commit()


def test_one_mail_per_forwarder_with_dates_and_link(client, db_session, sent_mails):
    headers = login(client)
    fid = _forwarder_id(client, headers)
    _set_email(db_session, fid, "spedycja@example.com")
    a = _create(client, headers, _no("100001"), eta=_d("2026-10-01"), forwarder_id=fid)
    b = _create(client, headers, _no("100002"), eta=_d("2026-10-02"), forwarder_id=fid)
    body = _send(client, headers, [a["id"], b["id"]])
    assert body["sent"] == 2 and body["failed"] == [] and body["missing_email"] == []
    assert body["emailed"] == [{"forwarder": body["emailed"][0]["forwarder"],
                                "email": "spedycja@example.com", "containers": 2}]
    assert len(sent_mails) == 1
    to, subject, html = sent_mails[0]
    assert to == ["spedycja@example.com"] and "2 kont." in subject
    assert a["container_no"] in html and b["container_no"] in html
    assert "https://kolejka.example/spedycja" in html
    assert "DOSTAWCA" not in html   # spedytor nie dostaje danych dostawcy
    notes = [r.note for r in db_session.query(AuditLog).filter_by(field="plan_mail")]
    assert len(notes) == 2


def test_missing_email_reported_and_status_kept(client, db_session, sent_mails):
    headers = login(client)
    fid = _forwarder_id(client, headers)
    _set_email(db_session, fid, "")
    c = _create(client, headers, _no("100003"), eta=_d("2026-10-01"), forwarder_id=fid)
    body = _send(client, headers, [c["id"]])
    assert body["sent"] == 1 and len(body["missing_email"]) == 1 and sent_mails == []
    db_session.expire_all()
    assert db_session.get(Container, c["id"]).planning_status == PlanningStatus.WYSLANE


def test_mail_failure_is_explicit(client, db_session, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("SMTP nie jest skonfigurowany (SMTP_HOST).")
    monkeypatch.setattr(plan_mail, "send_html_email", boom)
    headers = login(client)
    fid = _forwarder_id(client, headers)
    _set_email(db_session, fid, "spedycja@example.com")
    c = _create(client, headers, _no("100004"), eta=_d("2026-10-01"), forwarder_id=fid)
    body = _send(client, headers, [c["id"]])
    assert body["emailed"] == [] and "SMTP" in body["failed"][0]["error"]
    db_session.expire_all()
    assert db_session.get(Container, c["id"]).planning_status == PlanningStatus.WYSLANE


def test_confirmed_plan_not_mailed_again(client, db_session, sent_mails):
    headers = login(client)
    fid = _forwarder_id(client, headers)
    _set_email(db_session, fid, "spedycja@example.com")
    c = _create(client, headers, _no("100005"), eta=_d("2026-10-01"), forwarder_id=fid)
    db_session.get(Container, c["id"]).planning_status = PlanningStatus.POTWIERDZONE
    db_session.commit()
    body = _send(client, headers, [c["id"]])
    assert body["skipped"] == [c["container_no"]] and sent_mails == []
