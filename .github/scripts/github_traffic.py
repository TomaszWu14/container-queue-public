"""Cotygodniowy push (ntfy) z ruchem w publicznych repo portfolio (Traffic API GitHuba).

Tylko stdlib. Sekrety z env: TRAFFIC_TOKEN (fine-grained PAT, Administration: Read-only),
NTFY_URL (pełny URL tematu), opcjonalnie NTFY_TOKEN; TRAFFIC_REPOS nadpisuje listę repo.
Bez TRAFFIC_TOKEN lub NTFY_URL — komunikat i exit 0 (workflow zielony przed konfiguracją).
`--dry-run` wypisuje wiadomość zamiast wysyłać.
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

OWNER = "TomaszWu14"
REPOS = ("container-queue-public", "twinema-public", "palviz-public", "miniWMS-public",
         "trash-fairy", "rcp-log-public", "hugme", "doc.compare-public", "flowmap",
         "artwork-checker-public")
API = "https://api.github.com/repos/{owner}/{repo}/traffic/{kind}"
TIMEOUT_S = 15
DAYS = 7
MAX_BODY = 3500
TITLE = "Ruch na GitHubie (7 dni)"


def _get(url: str, token: str):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "github-traffic-report"})
    # nosec B310 — URL stały (https://api.github.com), schemat nie pochodzi z danych wejściowych
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:  # nosec B310
        return json.load(resp)


def sum_last_days(items: list, today: dt.date, days: int = DAYS) -> tuple[int, int]:
    """Suma (count, uniques) z ostatnich `days` pełnych dni UTC — bez dzisiejszego (niepełnego)."""
    start = today - dt.timedelta(days=days)
    count = uniques = 0
    for it in items:
        day = dt.date.fromisoformat(it["timestamp"][:10])
        if start <= day < today:
            count += it.get("count", 0)
            uniques += it.get("uniques", 0)
    return count, uniques


def repo_stats(owner: str, repo: str, token: str, today: dt.date) -> dict:
    url = lambda kind: API.format(owner=owner, repo=repo, kind=kind)  # noqa: E731
    try:
        views = _get(url("views"), token).get("views", [])
        clones = _get(url("clones"), token).get("clones", [])
        refs = _get(url("popular/referrers"), token)
    except urllib.error.HTTPError as exc:
        return {"repo": repo, "error": "brak dostępu (sprawdź token)"
                if exc.code in (401, 403, 404) else f"błąd HTTP {exc.code}"}
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return {"repo": repo, "error": f"błąd ({type(exc).__name__})"}
    v, vu = sum_last_days(views, today)
    c, _ = sum_last_days(clones, today)
    top = sorted(refs, key=lambda r: r.get("count", 0), reverse=True)[:3]
    return {"repo": repo, "views": v, "uniques": vu, "clones": c,
            "refs": [(r.get("referrer", "?"), r.get("count", 0)) for r in top]}


def build_message(stats: list) -> str:
    ok = [s for s in stats if "error" not in s]
    lines = [f"Razem: {sum(s['views'] for s in ok)} wyświetleń "
             f"({sum(s['uniques'] for s in ok)} osób), {sum(s['clones'] for s in ok)} klonowań",
             "(źródła = ostatnie 14 dni)", ""]
    active = sorted((s for s in ok if s["views"] or s["clones"]),
                    key=lambda s: (s["views"], s["clones"]), reverse=True)
    for s in active:
        line = f"{s['repo']}: {s['views']} wyśw. ({s['uniques']} os.), {s['clones']} klon."
        if s["refs"]:
            line += " · skąd: " + ", ".join(f"{name} {n}" for name, n in s["refs"])
        lines.append(line)
    if not active:
        lines.append("Brak ruchu w repo.")
    lines += [f"{s['repo']}: {s['error']}" for s in stats if "error" in s]
    body = "\n".join(lines)
    return body if len(body) <= MAX_BODY else body[:MAX_BODY - 1] + "…"


def send(url: str, body: str, token: str = "") -> None:
    headers = {"Title": TITLE, "Tags": "bar_chart", "Content-Type": "text/plain; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")
    # nosec B310 — schemat NTFY_URL sprawdzony w main() (tylko http/https)
    with urllib.request.urlopen(req, timeout=TIMEOUT_S):  # nosec B310
        pass


def main(argv: list | None = None) -> int:
    dry = "--dry-run" in (argv if argv is not None else sys.argv[1:])
    token = os.environ.get("TRAFFIC_TOKEN", "").strip()
    ntfy = os.environ.get("NTFY_URL", "").strip()
    if not token or (not ntfy and not dry):
        print("Brak TRAFFIC_TOKEN lub NTFY_URL — raport pominięty (skonfiguruj sekrety).")
        return 0
    if ntfy and not ntfy.lower().startswith(("https://", "http://")):
        print("NTFY_URL musi zaczynać się od https:// lub http:// — raport pominięty.")
        return 0
    repos = [r.strip() for r in os.environ.get("TRAFFIC_REPOS", "").split(",") if r.strip()]
    today = dt.datetime.now(dt.UTC).date()
    body = build_message([repo_stats(OWNER, r, token, today) for r in repos or REPOS])
    if dry:
        print(f"{TITLE}\n\n{body}")
        return 0
    send(ntfy, body, os.environ.get("NTFY_TOKEN", "").strip())
    print("Wysłano raport ruchu do ntfy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
