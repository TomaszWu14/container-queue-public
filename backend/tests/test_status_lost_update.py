"""US-003 (R-02, P-13, ADR-0003): przejście statusu na podstawie nieaktualnego widoku dostaje 409
zamiast po cichu nadpisać cudzą zmianę. Kontener, odprawa, zlecenie transportowe; bez oczekiwanej
wartości (stary klient, import, n8n) — jak dotąd."""
from .conftest import login
from .test_forwarding import _setup


def _container(client, admin_headers, no="TCNU0000011"):
    company_id = client.get("/api/companies", headers=admin_headers).json()[0]["id"]
    r = client.post("/api/containers", headers=admin_headers,
                    json={"container_no": no, "company_id": company_id})
    assert r.status_code in (200, 201), r.text
    return r.json()


def test_container_status_on_stale_view_is_409(client, admin_headers):
    c = _container(client, admin_headers)
    url, seen = f"/api/containers/{c['id']}/status", c["status"]
    first = client.post(url, headers=admin_headers, json={"status": "W_PRODUKCJI", "expected_status": seen})
    assert first.status_code == 200, first.text
    second = client.post(url, headers=admin_headers,
                         json={"status": "W_TRANSPORCIE", "expected_status": seen})
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "state_changed"
    assert second.json()["detail"]["current"] == "W_PRODUKCJI"
    assert client.get(f"/api/containers/{c['id']}", headers=admin_headers).json()["status"] == "W_PRODUKCJI"


def test_container_status_unrelated_edit_is_not_a_conflict(client, admin_headers):
    """Notatka zmieniona w międzyczasie nie blokuje statusu (inaczej niż expected_updated_at)."""
    c = _container(client, admin_headers)
    assert client.patch(f"/api/containers/{c['id']}", headers=admin_headers,
                        json={"notes": "ktoś inny"}).status_code == 200
    r = client.post(f"/api/containers/{c['id']}/status", headers=admin_headers,
                    json={"status": "W_PRODUKCJI", "expected_status": c["status"]})
    assert r.status_code == 200, r.text


def test_container_status_without_expected_works_as_before(client, admin_headers):
    c = _container(client, admin_headers)
    r = client.post(f"/api/containers/{c['id']}/status", headers=admin_headers, json={"status": "W_PRODUKCJI"})
    assert r.status_code == 200, r.text


def test_customs_status_on_stale_view_is_409(client, admin_headers):
    c = _container(client, admin_headers)
    url = f"/api/customs/containers/{c['id']}/status"
    first = client.post(url, headers=admin_headers, json={
        "customs_status": "DOKUMENTY_KOMPLETNE", "expected_customs_status": "BRAK"})
    assert first.status_code == 200, first.text
    second = client.post(url, headers=admin_headers, json={
        "customs_status": "ZLECONA", "expected_customs_status": "BRAK"})
    assert second.status_code == 409
    assert second.json()["detail"]["current"] == "DOKUMENTY_KOMPLETNE"
    after = client.get(f"/api/containers/{c['id']}", headers=admin_headers).json()
    assert after["customs_status"] == "DOKUMENTY_KOMPLETNE"
    ok = client.post(url, headers=admin_headers, json={"customs_status": "ZLECONA"})   # stary klient
    assert ok.status_code == 200, ok.text


def test_transport_order_status_on_stale_view_is_409(client, admin_headers):
    ctx = _setup(client, admin_headers)
    logistics = login(client, "log.borealis", "haslo123")
    forwarder = login(client, "sped.spedalfa", "haslo123")
    order = client.post("/api/transport-orders", headers=logistics, json={
        "container_id": ctx["container"]["id"], "pickup_location": "DCT Gdańsk",
        "delivery_location": "Magazyn Borealis", "pickup_date": "2026-07-06"}).json()
    url = f"/api/transport-orders/{order['id']}/status"
    first = client.post(url, headers=forwarder, json={"status": "ZAAKCEPTOWANE", "expected_status": "WYSTAWIONE"})
    assert first.status_code == 200, first.text
    # logistyka na starym widoku chce zaakceptować w imieniu spedytora — już zaakceptowane
    second = client.post(url, headers=logistics, json={
        "status": "ZAAKCEPTOWANE", "reason": "potwierdził telefonicznie", "expected_status": "WYSTAWIONE"})
    assert second.status_code == 409
    assert second.json()["detail"]["current"] == "ZAAKCEPTOWANE"
