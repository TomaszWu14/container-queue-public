"""Trzecia lista PO, pkt 4: historia zmian reguł (kto, kiedy, co) i przywrócenie jednej reguły do stanu
sprzed wybranej zmiany — dodanie cofa się usunięciem, usunięcie przywraca regułę, zmiana wraca do starych pól."""


def _rule(**kw):
    return {"name": "Brak kierowcy", "condition": "no_driver", "days": 2, **kw}


def test_history_and_restore(client, admin_headers):
    r = client.put("/api/automations/rules", headers=admin_headers, json={"rules": [_rule()]})
    rid = r.json()["rules"][0]["id"]
    client.put("/api/automations/rules", headers=admin_headers,
               json={"rules": [_rule(id=rid, days=5, notify="admins")]})
    client.put("/api/automations/rules", headers=admin_headers, json={"rules": []})

    hist = client.get("/api/automations/rules/history", headers=admin_headers).json()
    assert [h["action"] for h in hist[:3]] == ["removed", "changed", "added"]
    assert set(hist[1]["changed"]) == {"days", "notify"} and hist[1]["user"]

    # przywróć stan sprzed usunięcia → reguła wraca z dniami 5
    r = client.post(f"/api/automations/rules/history/{hist[0]['id']}/restore", headers=admin_headers)
    assert r.status_code == 200 and [x["days"] for x in r.json()["rules"]] == [5]
    # przywróć stan sprzed zmiany → dni 2, ten sam identyfikator
    r = client.post(f"/api/automations/rules/history/{hist[1]['id']}/restore", headers=admin_headers)
    assert [(x["id"], x["days"], x["notify"]) for x in r.json()["rules"]] == [(rid, 2, "watchers")]
    # przywróć stan sprzed dodania → reguły nie ma
    r = client.post(f"/api/automations/rules/history/{hist[2]['id']}/restore", headers=admin_headers)
    assert r.json()["rules"] == []
    newest = client.get("/api/automations/rules/history", headers=admin_headers).json()[0]
    assert newest["note"].startswith("przywrócono stan sprzed zmiany")
    assert client.post("/api/automations/rules/history/999999/restore", headers=admin_headers).status_code == 404
