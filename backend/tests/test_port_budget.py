"""Budżet kosztów transportu i portu (czwarta lista PO, pkt 7, US-084)."""
import datetime

import pytest

from app import nbp, port_budget
from app.database import SessionLocal
from app.models import Company, FreightInvoice, User, utcnow


@pytest.fixture(autouse=True)
def _rates(monkeypatch):
    # kursy NBP bez sieci: 1 EUR = 4 PLN, 1 USD = 3.6 PLN; CNY bez kursu
    monkeypatch.setattr(nbp, "get_rates", lambda now=None: ({"EUR": 4.0, "USD": 3.6, "PLN": 1.0}, "2026-10-19"))


def _invoice(db, company_id, amount, currency="EUR", status="NOWA", days_ago=0):
    db.add(FreightInvoice(company_id=company_id, amount=amount, currency=currency, status=status,
                          created_at=utcnow() - datetime.timedelta(days=days_ago)))


def test_spent_forecast_and_states(client):
    today = datetime.date(2026, 10, 10)
    with SessionLocal() as db:
        co_id = db.query(Company).filter_by(code="ACME").one().id
        port_budget.set_budget(db, co_id, 10_000)
        _invoice(db, co_id, 2000)
        _invoice(db, co_id, 1000, "USD")                 # 900 EUR
        _invoice(db, co_id, 5000, status="ODRZUCONA")    # nie liczy się
        _invoice(db, co_id, 300, "CNY")                  # bez kursu → osobno
        db.flush()
        admin = db.query(User).filter_by(login="admin").one()
        rows = {r["company_id"]: r for r in port_budget.status(db, admin, today)["companies"]}
        db.rollback()
    acme = rows[co_id]
    assert acme["spent_eur"] == 2900.0 and acme["unconverted"] == 1
    assert acme["forecast_eur"] == round(2900 / 10 * 31, 2)
    assert acme["state"] == "ok"                          # 8990 < 90% z 10000
    other = next(r for r in rows.values() if r["company_id"] != co_id)
    assert other["state"] == "none"


def test_states_warn_and_over():
    assert port_budget.WARN_RATIO == 0.9
    with SessionLocal() as db:
        co = db.query(Company).first()
        port_budget.set_budget(db, co.id, 1000)
        _invoice(db, co.id, 400)
        db.flush()
        admin = db.query(User).filter_by(login="admin").one()
        warn = next(r for r in port_budget.status(db, admin, datetime.date(2026, 10, 10))["companies"]
                    if r["company_id"] == co.id)
        _invoice(db, co.id, 700)
        db.flush()
        over = next(r for r in port_budget.status(db, admin, datetime.date(2026, 10, 10))["companies"]
                    if r["company_id"] == co.id)
        db.rollback()
    assert warn["state"] == "warn" and over["state"] == "over"


def test_set_budget_admin_only_with_audit(client, admin_headers):
    companies = client.get("/api/companies", headers=admin_headers).json()
    cid = companies[0]["id"]
    r = client.put(f"/api/budgets/port/{cid}", json={"amount_eur": 12500}, headers=admin_headers)
    assert r.status_code == 200, r.text
    assert r.json()["budget_eur"] == 12500.0
    view = client.get("/api/budgets/port", headers=admin_headers).json()
    assert any(row["company_id"] == cid and row["budget_eur"] == 12500.0 for row in view["companies"])
    assert client.put(f"/api/budgets/port/{cid}", json={"amount_eur": -1}, headers=admin_headers).status_code == 422
    assert client.put("/api/budgets/port/999999", json={"amount_eur": 1}, headers=admin_headers).status_code == 404
    r = client.put(f"/api/budgets/port/{cid}", json={"amount_eur": None}, headers=admin_headers)
    assert r.json()["budget_eur"] is None
