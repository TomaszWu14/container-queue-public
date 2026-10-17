"""GET /freight-invoices?container_id= — faktury frachtowe jednego kontenera (zakładka
„Koszty" szuflady kolejki) z izolacją dostępu do kontenera."""
from sqlalchemy import select

from app.models import Company, Container, FreightInvoice, FreightInvoiceContainer
from tests.test_api import _make_user

from .conftest import login


def _setup(db):
    beta = db.scalar(select(Company).where(Company.code == "BETA"))
    gamma = db.scalar(select(Company).where(Company.code == "GAMMA"))
    a = Container(company_id=beta.id, container_no="MSCU7654321")
    b = Container(company_id=beta.id, container_no="MSDU0806613")
    other = Container(company_id=gamma.id, container_no="CSQU3054383")
    db.add_all([a, b, other])
    db.flush()
    shared = FreightInvoice(company_id=beta.id, bl_number="BL1", amount=1000, currency="USD")
    shared.items = [FreightInvoiceContainer(container_id=a.id), FreightInvoiceContainer(container_id=b.id)]
    only_b = FreightInvoice(company_id=beta.id, bl_number="BL2", amount=300, currency="EUR")
    only_b.items = [FreightInvoiceContainer(container_id=b.id)]
    db.add_all([shared, only_b])
    db.commit()
    return beta.id, a.id, b.id, other.id


def test_filter_by_container(client, db_session, admin_headers):
    _, a, b, _ = _setup(db_session)
    rows_a = client.get(f"/api/freight-invoices?container_id={a}", headers=admin_headers).json()
    assert [r["bl_number"] for r in rows_a] == ["BL1"]
    assert rows_a[0]["amount_per_container"] == 500
    rows_b = client.get(f"/api/freight-invoices?container_id={b}", headers=admin_headers).json()
    assert sorted(r["bl_number"] for r in rows_b) == ["BL1", "BL2"]
    assert len(client.get("/api/freight-invoices", headers=admin_headers).json()) == 2


def test_container_outside_scope_is_404(client, db_session, admin_headers):
    beta, _, _, other = _setup(db_session)
    _make_user(client, admin_headers, "log.beta", "logistics", beta)
    hdr = login(client, "log.beta", "haslo123")
    assert client.get(f"/api/freight-invoices?container_id={other}", headers=hdr).status_code == 404
