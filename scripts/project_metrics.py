"""Metryki projektu dla strony „Jak to zbudowano” (czwarta lista PO, pkt 13, US-080).

Liczy z repozytorium (bez sieci i bez bazy): testy backendu, frontendu i E2E, trasy API, historyjki wdrożone,
decyzje architektoniczne (ADR), języki interfejsu i numer ostatniego PR-a. Wynik:
`frontend/src/data/projectMetrics.json` — strona czyta go przy budowie, więc demo pokazuje liczby z dnia
wygenerowania (data jest na stronie). Odświeżenie z katalogu głównego:  python3 scripts/project_metrics.py
Generowane na żądanie (jak dokumentacja API), żeby równoległe PR-y nie zderzały się na tym pliku."""
import datetime
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend" / "src" / "data" / "projectMetrics.json"


def _count(pattern: str, files) -> int:
    rx = re.compile(pattern, re.M)
    return sum(len(rx.findall(p.read_text(encoding="utf-8", errors="ignore"))) for p in files)


def _frontend_test_files():
    src = ROOT / "frontend" / "src"
    return [p for p in src.rglob("*.test.ts*") if "node_modules" not in p.parts]


def _last_pr() -> int:
    try:
        log = subprocess.run(["git", "log", "--format=%s", "-n", "400"], cwd=ROOT, capture_output=True,  # nosec B603 B607
                             text=True, check=False).stdout
    except OSError:
        return 0
    return max((int(n) for n in re.findall(r"\(#(\d+)\)\s*$", log, re.M)), default=0)


def collect() -> dict:
    backend_tests = _count(r"^\s*(?:async\s+)?def test_\w+", (ROOT / "backend" / "tests").rglob("test_*.py"))
    frontend_tests = _count(r"^\s*(?:it|test)(?:\.each\([^)]*\))?\(\s*['`\"]", _frontend_test_files())
    e2e_tests = _count(r"^\s*test\(\s*['`\"]", (ROOT / "frontend" / "e2e").rglob("*.spec.ts"))
    spec = ROOT / "docs" / "architektura" / "openapi.json"
    api_ops = sum(len(ops) for ops in json.loads(spec.read_text(encoding="utf-8"))["paths"].values()) \
        if spec.exists() else 0
    stories = (ROOT / "docs" / "analiza" / "HISTORYJKI.md").read_text(encoding="utf-8")
    shipped = len(re.findall(r"^- \*\*Stan:\*\* wdrożone", stories, re.M))
    adrs = len([p for p in (ROOT / "docs" / "architektura" / "adr").glob("0*.md")])
    langs = len(re.findall(r"^\s+(pl|en|pt):", (ROOT / "frontend" / "src" / "i18n" / "features" /
                                                   "automatyzacje.ts").read_text(encoding="utf-8"), re.M))
    return {
        "generated_at": datetime.date.today().isoformat(),
        "backend_tests": backend_tests, "frontend_tests": frontend_tests, "e2e_tests": e2e_tests,
        "api_operations": api_ops, "stories_shipped": shipped, "adrs": adrs, "languages": langs,
        "last_pr": _last_pr(),
    }


def main() -> None:
    data = collect()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
