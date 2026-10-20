"""Przygotowanie wydania X.Y.Z (docs/WYDANIA.md): wersja w aplikacji + sekcja w CHANGELOG.

  python scripts/przygotuj_wydanie.py 0.2.0

- frontend/package.json, frontend/package-lock.json (pakiet główny), backend/app/main.py → X.Y.Z,
- CHANGELOG.md: treść [Unreleased] przechodzi do nowej sekcji [X.Y.Z] - dziś, [Unreleased] zostaje
  pusty, linki porównań na dole uzupełnione.
Potem PR, scalenie, tag `vX.Y.Z` na main — resztę robi workflow „Wydanie”."""
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = "https://github.com/TomaszWu14/container-queue-public"


def bump_files(version: str) -> None:
    pkg = ROOT / "frontend/package.json"
    data = json.loads(pkg.read_text(encoding="utf-8"))
    data["version"] = version
    pkg.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lock = ROOT / "frontend/package-lock.json"
    if lock.is_file():
        data = json.loads(lock.read_text(encoding="utf-8"))
        data["version"] = version
        data.get("packages", {}).get("", {})["version"] = version
        lock.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    main = ROOT / "backend/app/main.py"
    text, n = re.subn(r'version="[0-9.]+"', f'version="{version}"', main.read_text(encoding="utf-8"), count=1)
    if n != 1:
        raise SystemExit("backend/app/main.py: nie znalazłem version=\"…\"")
    main.write_text(text, encoding="utf-8")


def changelog(text: str, version: str, today: datetime.date) -> str:
    if f"## [{version}]" in text:
        raise SystemExit(f"CHANGELOG.md ma już sekcję [{version}]")
    head, sep, rest = text.partition("## [Unreleased]\n")
    if not sep:
        raise SystemExit("CHANGELOG.md: brak sekcji ## [Unreleased]")
    prev = re.search(r"^## \[([0-9.]+)\]", rest, re.M)
    if prev is None:
        raise SystemExit("CHANGELOG.md: brak poprzedniej wersji")
    body = rest[:prev.start()].strip("\n")
    if not body:
        raise SystemExit("[Unreleased] jest puste — nie ma czego wydawać")
    out = f"{head}## [Unreleased]\n\n## [{version}] - {today.isoformat()}\n\n{body}\n\n{rest[prev.start():]}"
    out = re.sub(r"^\[Unreleased\]: .*$", f"[Unreleased]: {REPO}/compare/v{version}...HEAD\n"
                 f"[{version}]: {REPO}/compare/v{prev.group(1)}...v{version}", out, count=1, flags=re.M)
    return out


def main(argv: list[str]) -> None:
    if len(argv) != 1 or not re.fullmatch(r"\d+\.\d+\.\d+", argv[0]):
        raise SystemExit("użycie: python scripts/przygotuj_wydanie.py X.Y.Z")
    version = argv[0]
    path = ROOT / "CHANGELOG.md"
    path.write_text(changelog(path.read_text(encoding="utf-8"), version, datetime.date.today()),
                    encoding="utf-8")
    bump_files(version)
    print(f"Gotowe: wersja {version}. Teraz PR → scalenie → tag v{version} na main.")


if __name__ == "__main__":
    main(sys.argv[1:])
