"""Druga lista PO, pkt 6: admin włącza / wyłącza automat jednym przełącznikiem — pętla zadań go pomija,
katalog pokazuje „wyłączony”, zmiana jest w dzienniku zmian; automatów chroniących dane nie da się wyłączyć."""
from app import jobs
from app.database import SessionLocal
from app.models import AuditLog

from .conftest import login


def _item(client, headers, key):
    return next(i for i in client.get("/api/automations", headers=headers).json()["items"] if i["key"] == key)


def test_switch_off_and_on_with_audit(client, admin_headers):
    assert _item(client, admin_headers, "forecast")["can_disable"] is True
    r = client.put("/api/automations/forecast/enabled", headers=admin_headers, json={"enabled": False})
    assert r.status_code == 200
    item = _item(client, admin_headers, "forecast")
    assert item["switched_off"] is True and item["status"] == "off"
    def check_demurrage_alerts(db):                                          # inny automat działa
        return 7
    assert jobs._run_fn(check_demurrage_alerts) == 7
    def check_forecast_alerts(db):                                           # ta sama nazwa co w katalogu
        raise AssertionError("wyłączony automat nie może się uruchomić")
    assert jobs._run_fn(check_forecast_alerts) is jobs.DISABLED
    client.put("/api/automations/forecast/enabled", headers=admin_headers, json={"enabled": True})
    assert _item(client, admin_headers, "forecast")["switched_off"] is False
    with SessionLocal() as db:
        changes = [(a.old_value, a.new_value) for a in db.query(AuditLog).filter_by(
            entity_type="automation", field="enabled.forecast").order_by(AuditLog.id)]
    assert changes == [("tak", "nie"), ("nie", "tak")]


def test_protected_and_unknown_and_non_admin(client, admin_headers):
    assert _item(client, admin_headers, "driver_data_purge")["can_disable"] is False
    assert client.put("/api/automations/driver_data_purge/enabled", headers=admin_headers,
                      json={"enabled": False}).status_code == 422
    assert client.put("/api/automations/nie-ma/enabled", headers=admin_headers,
                      json={"enabled": False}).status_code == 422
    assert _item(client, admin_headers, "mail_intake")["can_disable"] is False      # obieg z n8n
    from app.models import Role, User
    from app.security import hash_password
    with SessionLocal() as db:
        db.add(User(login="sw-logi", hashed_password=hash_password("pass12345"), role=Role.logistics))
        db.commit()
    assert client.put("/api/automations/forecast/enabled", headers=login(client, "sw-logi", "pass12345"),
                      json={"enabled": False}).status_code == 403
