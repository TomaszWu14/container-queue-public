"""US-005 (R-06, SR-002): link wywołań palet (DLT) ma tę samą ochronę co formularz awizacji —
limit żądań na IP (429 z Retry-After), dla POST tylko JSON z naszego Origin; wolne sloty awizacji
tylko dla dat w oknie ± 30 dni (od dziś albo od terminu z zaproszenia)."""
import datetime

from app.public_guards import PUBLIC_LIMIT_PER_MINUTE
from app.routers.avizo import SLOTS_WINDOW_DAYS
from tests.test_avizo_slots import DAY, _setup
from tests.test_dlt_confirm import _mock_powerbi, _send_call  # noqa: F401 — fixture


def test_dlt_rate_limited_with_retry_after(client, admin_headers, monkeypatch):
    _, token = _send_call(client, admin_headers, monkeypatch)
    codes = [client.get(f"/api/dlt/{token}").status_code for _ in range(PUBLIC_LIMIT_PER_MINUTE + 1)]
    assert codes[:PUBLIC_LIMIT_PER_MINUTE] == [200] * PUBLIC_LIMIT_PER_MINUTE
    last = client.get(f"/api/dlt/{token}")
    assert last.status_code == 429 and int(last.headers["Retry-After"]) > 0


def test_dlt_post_requires_json_from_our_origin(client, admin_headers, monkeypatch):
    _, token = _send_call(client, admin_headers, monkeypatch)
    foreign = client.post(f"/api/dlt/{token}/prepared", json={},
                          headers={"Origin": "https://evil.example"})
    assert foreign.status_code == 403
    assert client.post(f"/api/dlt/{token}/prepared", data={"x": "1"}).status_code == 415
    assert client.post(f"/api/dlt/{token}/prepared", json={}).status_code == 200


def test_dlt_link_not_leaked_in_referer_or_indexed(client, admin_headers, monkeypatch):
    _, token = _send_call(client, admin_headers, monkeypatch)
    resp = client.get(f"/api/dlt/{token}")
    assert resp.headers["Referrer-Policy"] == "no-referrer"
    assert "noindex" in resp.headers["X-Robots-Tag"]


def test_avizo_slots_only_within_window(client):
    raw = "swin" * 12
    _, a_id, _, _ = _setup(raw, cap=2)

    def slots(day):
        return client.get(f"/api/avizo/{raw}/slots", params={"container_id": a_id, "date": day.isoformat()})

    assert slots(DAY + datetime.timedelta(days=SLOTS_WINDOW_DAYS)).status_code == 200
    assert slots(datetime.date.today()).status_code == 200
    far = DAY + datetime.timedelta(days=SLOTS_WINDOW_DAYS + 40)
    resp = slots(far)
    assert resp.status_code == 422 and f"± {SLOTS_WINDOW_DAYS} dni" in resp.json()["detail"]
    assert slots(datetime.date(2000, 1, 1)).status_code == 422
