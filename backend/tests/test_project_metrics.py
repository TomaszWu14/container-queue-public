"""Metryki projektu (US-080): skrypt liczy z repozytorium dodatnie liczby i datę."""
import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "project_metrics.py"


def test_collect_counts_everything():
    spec = importlib.util.spec_from_file_location("project_metrics", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    data = mod.collect()
    for key in ("backend_tests", "frontend_tests", "e2e_tests", "api_operations", "stories_shipped", "adrs"):
        assert data[key] > 0, key
    assert data["languages"] == 3
    assert data["backend_tests"] > 1000
