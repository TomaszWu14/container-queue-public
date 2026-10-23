"""Cotygodniowy raport ruchu z GitHuba (.github/scripts/github_traffic.py) — bez sieci."""
import datetime as dt
import importlib.util
import io
import json
import pathlib
import urllib.error

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / ".github" / "scripts" / "github_traffic.py"
TODAY = dt.date(2026, 10, 19)


@pytest.fixture
def gt():
    spec = importlib.util.spec_from_file_location("github_traffic", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _days(*pairs, start=TODAY - dt.timedelta(days=8)):
    return [{"timestamp": f"{start + dt.timedelta(days=i)}T00:00:00Z", "count": c, "uniques": u}
            for i, (c, u) in enumerate(pairs)]


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _fake_urlopen(data: dict, sent: list):
    def urlopen(req, timeout):
        assert timeout == 15
        if req.get_method() == "POST":
            sent.append(req)
            return _Resp(b"")
        assert req.headers["Authorization"] == "Bearer tok"
        assert req.headers["X-github-api-version"] == "2022-11-28"
        repo, kind = req.full_url.split("/repos/TomaszWu14/")[1].split("/traffic/")
        if repo not in data:
            raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {}, None)
        return _Resp(json.dumps(data[repo][kind]).encode())
    return urlopen


def test_sums_only_last_seven_full_days(gt):
    # 8 dni temu (poza oknem), 7 dni w oknie po 1, dziś (niepełny dzień) poza oknem
    items = _days((100, 50), *[(1, 1)] * 7, (500, 9))
    assert gt.sum_last_days(items, TODAY) == (7, 7)


def test_message_sorted_desc_skips_idle_and_marks_no_access(gt):
    stats = [
        {"repo": "a", "views": 3, "uniques": 2, "clones": 0, "refs": []},
        {"repo": "idle", "views": 0, "uniques": 0, "clones": 0, "refs": []},
        {"repo": "palviz-public", "views": 40, "uniques": 12, "clones": 3,
         "refs": [("linkedin.com", 9), ("google.com", 4)]},
        {"repo": "x", "error": "brak dostępu (sprawdź token)"},
    ]
    lines = gt.build_message(stats).splitlines()
    assert lines[0] == "Razem: 43 wyświetleń (14 osób), 3 klonowań"
    assert "14 dni" in lines[1]
    body = lines[3:]
    assert body == ["palviz-public: 40 wyśw. (12 os.), 3 klon. · skąd: linkedin.com 9, google.com 4",
                    "a: 3 wyśw. (2 os.), 0 klon.", "x: brak dostępu (sprawdź token)"]


def test_body_truncated(gt):
    stats = [{"repo": f"r{i:03}" + "x" * 80, "views": 1, "uniques": 1, "clones": 0, "refs": []}
             for i in range(100)]
    assert len(gt.build_message(stats)) == gt.MAX_BODY


@pytest.mark.parametrize("env", [{}, {"TRAFFIC_TOKEN": "tok"}, {"NTFY_URL": "https://ntfy.sh/t"}])
def test_missing_secrets_exit_zero_without_network(gt, monkeypatch, env):
    for k in ("TRAFFIC_TOKEN", "NTFY_URL", "NTFY_TOKEN", "TRAFFIC_REPOS"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setattr(gt.urllib.request, "urlopen", lambda *a, **k: pytest.fail("sieć"))
    assert gt.main([]) == 0


def test_non_http_ntfy_url_is_skipped(gt, monkeypatch):
    monkeypatch.setenv("TRAFFIC_TOKEN", "tok")
    monkeypatch.setenv("NTFY_URL", "file:///etc/passwd")
    monkeypatch.setattr(gt.urllib.request, "urlopen", lambda *a, **k: pytest.fail("sieć"))
    assert gt.main([]) == 0


def test_end_to_end_sends_ntfy(gt, monkeypatch):
    week = _days((0, 0), *[(2, 1)] * 7, start=dt.datetime.now(dt.UTC).date()
                 - dt.timedelta(days=8))
    data = {"hugme": {"views": {"views": week}, "clones": {"clones": week[:3]},
                      "popular/referrers": [{"referrer": "github.com", "count": 5},
                                            {"referrer": "google.com", "count": 7}]}}
    sent = []
    monkeypatch.setattr(gt.urllib.request, "urlopen", _fake_urlopen(data, sent))
    monkeypatch.setenv("TRAFFIC_TOKEN", "tok")
    monkeypatch.setenv("NTFY_URL", "https://ntfy.sh/tajny")
    monkeypatch.setenv("NTFY_TOKEN", "nt")
    monkeypatch.setenv("TRAFFIC_REPOS", "hugme, missing")
    assert gt.main([]) == 0
    (req,) = sent
    assert req.full_url == "https://ntfy.sh/tajny"
    assert req.headers["Title"] == "Ruch na GitHubie (7 dni)"
    assert req.headers["Tags"] == "bar_chart"
    assert req.headers["Authorization"] == "Bearer nt"
    body = req.data.decode("utf-8")
    assert "hugme: 14 wyśw. (7 os.), 4 klon. · skąd: google.com 7, github.com 5" in body
    assert "missing: brak dostępu (sprawdź token)" in body


def test_dry_run_prints_instead_of_sending(gt, monkeypatch, capsys):
    sent = []
    monkeypatch.setattr(gt.urllib.request, "urlopen", _fake_urlopen({}, sent))
    monkeypatch.setenv("TRAFFIC_TOKEN", "tok")
    monkeypatch.delenv("NTFY_URL", raising=False)
    monkeypatch.setenv("TRAFFIC_REPOS", "hugme")
    assert gt.main(["--dry-run"]) == 0
    assert not sent
    out = capsys.readouterr().out
    assert "Ruch na GitHubie (7 dni)" in out and "hugme: brak dostępu" in out
