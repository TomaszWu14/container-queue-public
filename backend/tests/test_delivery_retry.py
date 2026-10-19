"""US-022: nieudana wysyłka (e-mail, Teams, n8n) wraca do kolejki i jest ponawiana po 1, 5 i 30 min;
po ostatniej próbie trafia do „nie doszło” i do dziennika zadań; opis błędu bez adresów i treści."""
import httpx
import pytest

from app import applog, delivery_retry as R


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    monkeypatch.setattr(R, "AUTO_START", False)
    R.reset()
    yield
    R.reset()


def _http_error(code=503):
    req = httpx.Request("POST", "https://prod.powerautomate.example/trigger?sig=SEKRET")
    return httpx.HTTPStatusError("blad https://prod.powerautomate.example/trigger?sig=SEKRET", request=req,
                                 response=httpx.Response(code, request=req))


def test_retry_until_success(monkeypatch):
    jobs = []
    monkeypatch.setattr(applog, "record_job", lambda **kw: jobs.append(kw))
    calls = []

    def flaky(x):
        calls.append(x)
        if len(calls) < 3:
            raise _http_error()
    assert R.attempt("n8n", "Kontener w porcie", flaky, "zdarzenie") is False
    snap = R.snapshot(now=0)
    assert snap["pending"][0]["error"] == "HTTP 503" and "SEKRET" not in str(snap)
    assert R.process_due(now=10**9) == 1          # druga próba — znów błąd, wraca do kolejki
    assert R.snapshot()["pending"][0]["attempts"] == 2
    assert R.process_due(now=10**10) == 1         # trzecia — sukces
    assert calls == ["zdarzenie"] * 3 and R.snapshot()["pending"] == []
    assert jobs[-1]["ok"] is True and jobs[-1]["fn"] == "n8n"


def test_gives_up_after_last_delay(monkeypatch):
    jobs = []
    monkeypatch.setattr(applog, "record_job", lambda **kw: jobs.append(kw))

    def down():
        raise ConnectionRefusedError("smtp.example.com:587")
    R.attempt("email", "Raport tygodniowy", down)
    for k in range(len(R.DELAYS_S)):
        R.process_due(now=10**(9 + k))
    snap = R.snapshot()
    assert snap["pending"] == []
    assert snap["failed"][0]["label"] == "Raport tygodniowy" and snap["failed"][0]["attempts"] == 4
    assert snap["failed"][0]["error"] == "ConnectionRefusedError"     # bez adresu serwera
    assert jobs[-1]["ok"] is False and jobs[-1]["job"] == R.JOB_NAME


def test_success_first_time_is_not_queued():
    assert R.attempt("teams", "x", lambda: None) is True
    assert R.snapshot()["pending"] == []


def test_endpoint_admin_only(client, admin_headers):
    R.attempt("teams", "Alert", lambda: (_ for _ in ()).throw(RuntimeError("x")))
    r = client.get("/api/automations/deliveries", headers=admin_headers)
    assert r.status_code == 200 and r.json()["pending"][0]["channel"] == "teams"
