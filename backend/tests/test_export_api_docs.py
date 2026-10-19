"""Dokumentacja API w repo (czwarta lista PO, pkt 12, US-077): każda trasa ma kolumnę „kto ma dostęp”."""
import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_api_docs.py"


def _mod():
    spec = importlib.util.spec_from_file_location("export_api_docs", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_operation_has_roles_from_permission_matrix():
    from app.main import app
    mod = _mod()
    md = mod.render(app.openapi(), mod.permissions())
    assert "| ? |" not in md                                   # każda trasa jest w macierzy uprawnień
    assert "| GET | `/api/users/access-review` |" in md and "| admin |" in md
    assert "publiczna" in md                                   # logowanie / linki z tokenem


def test_permissions_parser_reads_roles():
    perms = _mod().permissions()
    assert perms["GET /api/users/access-review"] == "admin"
    assert "logistics" in perms["GET /api/automations/rules/backtest"]
