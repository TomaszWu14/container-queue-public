"""Top 15 PO, pkt 1: demo ma dane na ekranie „Automatyzacje” — automaty z historią przebiegów
(stan „działa”, efekty, oszczędność), przykładowe reguły i faktury dla panelu jakości odczytu AI."""
from tests.test_seed_demo_process import seeded  # noqa: F401 — fixture

from .conftest import login

PW = "Demo-Portfolio-2026"


def test_automations_screen_is_not_empty(seeded, client):  # noqa: F811
    h = login(client, "demo", PW)
    cat = client.get("/api/automations", headers=h).json()
    by_key = {i["key"]: i for i in cat["items"]}
    assert by_key["demurrage"]["status"] == "ok" and by_key["demurrage"]["runs"] > 0
    assert by_key["tracking"]["errors"] == 1 and by_key["tracking"]["status"] == "ok"
    assert cat["summary"]["effects"] > 0 and cat["summary"]["hours_saved"] > 0
    assert cat["summary"]["attention"] == 0
    assert by_key["outbound_events"]["runs"] > 0


def test_rules_and_ai_quality_have_data(seeded, client):  # noqa: F811
    h = login(client, "demo", PW)
    rules = client.get("/api/automations/rules", headers=h).json()["rules"]
    assert len(rules) == 3 and all(r["id"] for r in rules)
    q = client.get("/api/automations/ai-quality", headers=h).json()
    assert q["totals"]["items"] > 100
    assert sum(1 for w in q["weeks"] if w["rules"] + w["ml"] + w["user"] + w["open"]) >= 6
    assert 40 <= q["automated_pct"] <= 90 and q["totals"]["open"] > 0
    b = {x["bucket"]: x for x in q["buckets"]}
    assert b["auto"]["hit_pct"] > b["high"]["hit_pct"] > b["low"]["hit_pct"]   # kalibracja czytelna


def test_process_flow_is_realistic(seeded, client):  # noqa: F811
    """Historia statusów demo: kontenery w obiegu weszły w obecny etap niedawno, więc „dłużej niż zwykle”
    to wyjątki, a pierwszy etap liczy się od prawdziwego utworzenia (nie od chwili wgrania demo)."""
    body = client.get("/api/automations/process", headers=login(client, "demo", PW)).json()
    first = next(s for s in body["stages"] if s["status"] == "ZAPOWIEDZIANY")
    assert first["median_days"] and first["median_days"] > 0
    assert body["stuck_total"] <= 25 and body["transitions_total"] > 500
