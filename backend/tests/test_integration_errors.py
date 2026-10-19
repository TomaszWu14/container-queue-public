"""US-026 (T-08…T-12): nieoczekiwana odpowiedź integracji zewnętrznej daje czytelny komunikat albo pustą
wartość „niedostępne” — nigdy błąd 500 ani ciche dane z błędnej odpowiedzi."""
import datetime

import httpx
import pytest

from app import nbp, sharepoint
from app.config import settings
from app.tracking import ais

from .test_palletization import _make_container
from .test_weather_route import _Resp


def test_sharepoint_bad_json_is_readable_error(monkeypatch):
    """T-08: Graph zwraca HTML albo listę zamiast obiektu → SharePointError z opisem (panel integracji)."""
    sharepoint._site_ids.clear()
    monkeypatch.setattr(settings, "sharepoint_site", "firma.sharepoint.com:/sites/Log")

    class Html:
        status_code = 200

        def json(self):
            raise ValueError("not json")
    monkeypatch.setattr(sharepoint, "_get", lambda *a, **k: Html())
    with pytest.raises(sharepoint.SharePointError, match="nie jest JSON"):
        sharepoint.site_id("t")
    monkeypatch.setattr(sharepoint, "_get", lambda *a, **k: _Resp(["x"]))
    with pytest.raises(sharepoint.SharePointError, match="nieoczekiwany format"):
        sharepoint.site_id("t")
    monkeypatch.setattr(sharepoint, "_get", lambda *a, **k: _Resp({"name": "bez id"}))
    with pytest.raises(sharepoint.SharePointError, match="bez identyfikatora"):
        sharepoint.site_id("t")


@pytest.mark.parametrize("body", ["tekst", 42])
def test_palletization_bad_body_is_message_not_500(client, admin_headers, monkeypatch, body):
    """T-09: serwis paletyzacji zwraca nie-JSON albo liczbę → komunikat „niedostępny”."""
    monkeypatch.setattr(settings, "pallet_api_url", "https://pallets.example/api")

    class Bad:
        def raise_for_status(self):
            pass

        def json(self):
            if body == "tekst":
                raise ValueError("Expecting value")
            return body
    monkeypatch.setattr("app.routers.containers.httpx.get", lambda *a, **k: Bad())
    cid = _make_container(client, admin_headers)
    r = client.get(f"/api/containers/{cid}/palletization", headers=admin_headers)
    assert r.status_code == 200
    assert r.json() == {"configured": True, "error": "Serwis paletyzacji niedostępny."}


@pytest.mark.parametrize("frame", ['[1, 2]', '"tekst"', '{"MetaData": "zle"}', '7'])
def test_ais_odd_frame_is_skipped(db_session, frame):
    """T-10: ramka AIS innego kształtu niż słownik jest pomijana, obsługa idzie dalej."""
    assert ais.handle_message(db_session, frame, {}) is False


def test_weather_error_status_takes_error_path(client, db_session, monkeypatch):
    """T-11: open-meteo 400 {"error": true} → ścieżka błędu (krótki cache), nie „prognoza” z pustymi polami."""
    from app.models import TrackedVessel
    from app.tracking import weather

    from .test_weather_route import _active_container
    weather._cache.update(at=None, data=[])
    _active_container(client, "MV BLAD")
    db_session.add(TrackedVessel(name="MV BLAD", lat=35.0, lon=18.0))
    db_session.commit()
    monkeypatch.setattr("httpx.get", lambda *a, **k: _Resp({"error": True, "reason": "zle"}, status=400))
    assert weather.fetch_weather(db_session) == []
    assert weather._cache["ttl"] == weather.ERROR_TTL_S
    weather._cache.update(at=None, data=[])


def test_nbp_stale_rates_have_age_limit(monkeypatch):
    """T-12: przy awarii NBP ostatnie kursy tylko w granicy MAX_STALE; starsze = brak przeliczenia."""
    fetched = datetime.datetime(2026, 10, 1, 9, 0)
    monkeypatch.setattr(nbp, "_cache", (fetched, {"PLN": 1.0, "EUR": 4.3}, "2026-10-01"))

    def down():
        raise httpx.ConnectError("brak sieci")
    monkeypatch.setattr(nbp, "_fetch_rates", down)
    assert nbp.get_rates(fetched + datetime.timedelta(days=3))[1] == "2026-10-01"
    assert nbp.get_rates(fetched + nbp.MAX_STALE + datetime.timedelta(hours=1)) == ({}, None)
