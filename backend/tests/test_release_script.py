"""scripts/przygotuj_wydanie.py (docs/WYDANIA.md): [Unreleased] → [X.Y.Z], linki porównań, wersje."""
import datetime
import importlib.util
import pathlib

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "przygotuj_wydanie.py"
spec = importlib.util.spec_from_file_location("przygotuj_wydanie", SCRIPT)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

LOG = """# Changelog

## [Unreleased]

### Added
- coś nowego

## [0.1.0] - 2026-10-13

Start.

[Unreleased]: https://github.com/TomaszWu14/container-queue-public/compare/3373194...HEAD
[0.1.0]: https://github.com/TomaszWu14/container-queue-public/commit/3373194
"""


def test_unreleased_becomes_new_version_with_links():
    out = release.changelog(LOG, "0.2.0", datetime.date(2026, 10, 21))
    assert "## [Unreleased]\n\n## [0.2.0] - 2026-10-21\n\n### Added\n- coś nowego\n\n## [0.1.0]" in out
    assert "[Unreleased]: https://github.com/TomaszWu14/container-queue-public/compare/v0.2.0...HEAD" in out
    assert "[0.2.0]: https://github.com/TomaszWu14/container-queue-public/compare/v0.1.0...v0.2.0" in out
    assert "[0.1.0]: https://github.com/TomaszWu14/container-queue-public/commit/3373194" in out


def test_refuses_empty_or_duplicate_release():
    out = release.changelog(LOG, "0.2.0", datetime.date(2026, 10, 21))
    with pytest.raises(SystemExit):
        release.changelog(out, "0.3.0", datetime.date(2026, 10, 22))   # puste [Unreleased]
    with pytest.raises(SystemExit):
        release.changelog(out, "0.2.0", datetime.date(2026, 10, 22))


def test_real_changelog_and_versions_are_releasable():
    root = SCRIPT.parents[1]
    out = release.changelog((root / "CHANGELOG.md").read_text(encoding="utf-8"), "9.9.9", datetime.date.today())
    assert "## [9.9.9]" in out
    assert 'version="' in (root / "backend/app/main.py").read_text(encoding="utf-8")
