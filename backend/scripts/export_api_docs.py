"""Dokumentacja API do repozytorium (czwarta lista PO, pkt 12): `docs/architektura/openapi.json`
i `docs/architektura/API-TRASY.md` (konwencje i mapa zasobów: `docs/architektura/API.md`).

Produkcja nie publikuje /docs ani /openapi.json (świadoma decyzja — mniejsza powierzchnia na żywej instancji).
Kod jest jawny w repozytorium, więc ten sam opis jako plik nic nie odsłania, a recenzent i integrator (n8n,
Power Automate) widzą wszystkie trasy i to, które role mają do nich dostęp — z macierzy uprawnień
`tests/permissions.yaml`, której zgodność z kodem pilnuje test.

Uruchom z `backend/` po zmianie tras:  python scripts/export_api_docs.py
Plik jest generowany na żądanie (nie przy każdym PR-ze), żeby równoległe zmiany nie zderzały się na nim."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[2]
ROLES = ("admin", "logistics", "warehouse", "forwarder", "customs", "purchasing", "sales")
_LINE = re.compile(r'^\s+"(?P<key>[A-Z]+ /[^"]+)":\s*\{(?P<body>[^}]*)\}')


def permissions() -> dict[str, str]:
    """„GET /api/x” → „admin, logistics” albo „publiczna” — wprost z macierzy uprawnień."""
    out: dict[str, str] = {}
    for line in (ROOT / "tests" / "permissions.yaml").read_text(encoding="utf-8").splitlines():
        m = _LINE.match(line)
        if not m:
            continue
        cells = dict(part.strip().split(":", 1) for part in m["body"].split(",") if ":" in part)
        cells = {k.strip(): v.strip().strip("'\"") for k, v in cells.items()}
        if cells.get("anon") in ("public", "200", "2xx"):
            out[m["key"]] = "publiczna (link z tokenem / logowanie)"
            continue
        allowed = [r for r in ROLES if cells.get(r, "403") not in ("403", "401")]
        out[m["key"]] = ", ".join(allowed) if allowed else "—"
    return out


def render(spec: dict, perms: dict[str, str]) -> str:
    groups: dict[str, list[tuple[str, str, str, str]]] = defaultdict(list)
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            key = f"{method.upper()} {path}"
            # pierwsze zdanie docstringu (po polsku) zamiast nazwy funkcji z FastAPI
            doc = (op.get("description") or "").strip().split("\n")[0].strip()
            summary = (doc or op.get("summary") or "").replace("|", "/")[:140]
            groups[(op.get("tags") or ["inne"])[0]].append((method.upper(), path, summary, perms.get(key, "?")))
    total = sum(len(v) for v in groups.values())
    lines = [
        "# API — trasy i uprawnienia",
        "",
        "Wygenerowane z kodu: `python scripts/export_api_docs.py` (z `backend/`). Pełny opis z typami pól:",
        "[`openapi.json`](openapi.json) — można go wczytać w Swagger Editor, Postmanie albo n8n.",
        "Konwencje (logowanie, CSRF, błędy, stronicowanie): [API.md](API.md).",
        "",
        f"**{total} operacji w {len(groups)} grupach.** Kolumna „Kto ma dostęp” pochodzi z macierzy uprawnień",
        "([`tests/permissions.yaml`](../../tests/permissions.yaml)); zgodność macierzy z kodem sprawdza test.",
        "Dostęp do konkretnych rekordów zawęża dodatkowo zakres spółki / partnera (izolacja danych).",
        "Na produkcji `/docs` i `/openapi.json` są wyłączone — ten plik jest jedynym publicznym opisem.",
        "",
    ]
    for tag in sorted(groups):
        lines += [f"## {tag}", "", "| Metoda | Ścieżka | Opis | Kto ma dostęp |", "|---|---|---|---|"]
        lines += [f"| {m} | `{p}` | {s} | {r} |" for m, p, s, r in sorted(groups[tag], key=lambda x: (x[1], x[0]))]
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    from app.main import app
    spec = app.openapi()
    out = ROOT / "docs" / "architektura"
    (out / "openapi.json").write_text(json.dumps(spec, ensure_ascii=False, separators=(",", ":")) + "\n",
                                      encoding="utf-8")
    (out / "API-TRASY.md").write_text(render(spec, permissions()), encoding="utf-8")
    print(f"docs/architektura/API-TRASY.md + openapi.json: {len(spec['paths'])} ścieżek")


if __name__ == "__main__":
    main()
