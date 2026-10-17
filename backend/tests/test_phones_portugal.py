"""US-016 (P-05, P-06): kierowca portugalski dostaje SMS-a — 9-cyfrowy numer bierze kierunkowy kraju
magazynu (PL +48, PT +351); magazyn tworzony z kolejki dziedziczy kraj spółki zamiast zawsze PL."""
import pytest
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Container, Warehouse
from app.phones import normalize_phone
from app.sms import mock_outbox
from tests.test_avizo_public import make_request, outbox, stage1  # noqa: F401 — fixture
from tests.test_driver_link import _setup


@pytest.mark.parametrize("raw,country,expected", [
    ("600 100 200", "PL", "+48600100200"),
    ("912-345-678", "PT", "+351912345678"),
    ("912345678", None, "+48912345678"),            # brak magazynu = jak dotąd
    ("912345678", "DE", "+48912345678"),            # kraj spoza listy = PL
    ("+351 912 345 678", "PL", "+351912345678"),    # numer z kierunkowym zostaje
    ("0048 600 100 200", "PT", "+48600100200"),
])
def test_normalize_phone_uses_warehouse_country(raw, country, expected):
    assert normalize_phone(raw, country) == expected


@pytest.mark.parametrize("raw", ["abc", "12345", "+0 123"])
def test_normalize_phone_rejects_garbage(raw):
    with pytest.raises(ValueError, match=r"\+351"):
        normalize_phone(raw, "PT")


def _set_country(warehouse_id, country):
    with SessionLocal() as db:
        db.get(Warehouse, warehouse_id).country = country
        db.commit()


def test_sms_to_portuguese_driver_gets_351(client, admin_headers):
    container = _setup(client, admin_headers)
    with SessionLocal() as db:
        wh_id = db.get(Container, container["id"]).warehouse_id
    _set_country(wh_id, "PT")
    sent = client.post(f"/api/containers/{container['id']}/driver-sms", headers=admin_headers)
    assert sent.status_code == 200 and sent.json()["status"] == "sent", sent.text
    assert mock_outbox[-1]["phone"] == "+351600100200"


def test_sms_to_polish_driver_unchanged(client, admin_headers):
    container = _setup(client, admin_headers)
    client.post(f"/api/containers/{container['id']}/driver-sms", headers=admin_headers)
    assert mock_outbox[-1]["phone"] == "+48600100200"


def test_avizo_driver_form_saves_351_for_portuguese_warehouse(client, outbox, admin_headers):  # noqa: F811
    req_id, raw, ids = make_request(n=1)
    with SessionLocal() as db:
        c = db.get(Container, ids[0])
        wh = Warehouse(company_id=c.company_id, name="Armazém Porto", country="PT")
        db.add(wh)
        db.flush()
        c.warehouse_id = wh.id
        db.commit()
    assert client.post(f"/api/avizo/{raw}", json=stage1(ids)).status_code == 200
    assert client.post(f"/api/avizo-requests/{req_id}/approve", headers=admin_headers).status_code == 200
    link = outbox[-1].text.split("/avizo/driver/")[1].split()[0]
    resp = client.post(f"/api/avizo/driver/{link}", json={"items": [{
        "container_id": ids[0], "driver_name": "João Silva", "driver_phone": "912 345 678",
        "truck_no": "AA12BB", "trailer_no": ""}]})
    assert resp.status_code == 200, resp.text
    with SessionLocal() as db:
        assert db.get(Container, ids[0]).driver_phone == "+351912345678"


def test_new_warehouse_from_queue_inherits_company_country(client, admin_headers):
    companies = client.get("/api/companies", headers=admin_headers).json()
    company = next(c for c in companies if c["code"] == "BETA")
    with SessionLocal() as db:
        for wh in db.scalars(select(Warehouse).where(Warehouse.company_id == company["id"])):
            wh.country = "PT"
        if not db.scalar(select(Warehouse).where(Warehouse.company_id == company["id"])):
            db.add(Warehouse(company_id=company["id"], name="Armazém Lisboa", country="PT"))
        db.commit()
    created = client.post("/api/containers", headers=admin_headers, json={
        "container_no": "MSKU1234565", "company_id": company["id"]}).json()
    resp = client.post(f"/api/containers/{created['id']}/warehouse", headers=admin_headers,
                       json={"name": "Armazém Novo"})
    assert resp.status_code == 200, resp.text
    with SessionLocal() as db:
        assert db.scalar(select(Warehouse.country).where(Warehouse.name == "Armazém Novo")) == "PT"
