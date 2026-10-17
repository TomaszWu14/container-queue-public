"""US-015 (NFR-011): jedna wersja Pythona i Node — testy w CI biegną na tych samych wersjach, które
działają na produkcji (obraz Dockera), a README podaje te same. Lock zależności jest „universal” od
najniższej wspieranej wersji, więc nie może deklarować wersji wyższej niż obraz."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCKERFILES = ["backend/Dockerfile", "frontend/Dockerfile", "Dockerfile.coolify"]


def _versions(pattern: str, paths) -> set[str]:
    found = set()
    for path in paths:
        found.update(re.findall(pattern, (ROOT / path).read_text(encoding="utf-8")))
    return found


def _workflows():
    return sorted(p.relative_to(ROOT) for p in (ROOT / ".github/workflows").glob("*.yml"))


def test_ci_python_matches_production_image():
    image = _versions(r"FROM python:(\d+\.\d+)", DOCKERFILES)
    ci = _versions(r"python-version:\s*'(\d+\.\d+)'", _workflows())
    assert len(image) == 1 and ci == image, f"obraz {image}, CI {ci}"


def test_ci_node_matches_production_image():
    image = _versions(r"FROM node:(\d+)", DOCKERFILES)
    ci = _versions(r"node-version:\s*'(\d+)'", _workflows())
    assert len(image) == 1 and ci == image, f"obraz {image}, CI {ci}"


def test_readme_names_the_same_versions():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    (python,) = _versions(r"FROM python:(\d+\.\d+)", DOCKERFILES)
    (node,) = _versions(r"FROM node:(\d+)", DOCKERFILES)
    assert f"Python {python}" in readme and f"Node {node}" in readme


def test_lock_floor_not_above_image():
    (image,) = _versions(r"FROM python:(\d+\.\d+)", DOCKERFILES)
    for lock in ("backend/requirements.txt", "backend/requirements-dev.txt"):
        (floor,) = _versions(r"--python-version (\d+\.\d+)", [lock])
        assert tuple(map(int, floor.split("."))) <= tuple(map(int, image.split("."))), lock


def test_pre_commit_tools_match_ci():
    """US-007: lokalny pre-commit używa tych samych wersji Bandit, gitleaks i ruff co CI / lock."""
    pre_commit = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    security = (ROOT / ".github/workflows/security.yml").read_text(encoding="utf-8")
    lock = (ROOT / "backend/requirements-dev.txt").read_text(encoding="utf-8")

    def rev(repo: str) -> str:
        return re.search(rf"{repo}\s*\n\s*rev:\s*v?([\d.]+)", pre_commit).group(1)

    assert rev("PyCQA/bandit") == re.search(r'bandit\[toml\]==([\d.]+)', security).group(1)
    assert rev("gitleaks/gitleaks") == re.search(r"GITLEAKS_VERSION:\s*([\d.]+)", security).group(1)
    assert rev("astral-sh/ruff-pre-commit") == re.search(r"^ruff==([\d.]+)", lock, re.M).group(1)
