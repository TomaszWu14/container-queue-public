"""US-011 (R-01, SR-005): strażnik izolacji spółek dla nowych tras. Każda trasa `/api/...` z identyfikatorem
w ścieżce (`{..._id}`) musi przejść przez kontrolę z `deps.py` (`get_scoped`, `scope_*`,
`check_container_access` …) — w samej funkcji albo w funkcji pomocniczej, którą woła (do 2 poziomów) —
albo być na liście wyjątków z uzasadnieniem. Nowa trasa bez kontroli i bez wpisu = czerwony test.

Test jest heurystyką po źródle (szuka wywołań), nie dowodem: zakres i rolę każdej trasy sprawdza też
macierz `tests/permissions.yaml`, a izolację na danych — testy „obca spółka = 404”."""
import inspect
import re
import sys

from tests.test_routes_require_auth import _api_routes

GUARDS = re.compile(
    r"\b(get_scoped|get_company_scoped|scope_\w+|check_container_access|get_container_checked"
    r"|check_company_access|check_supplier_access|forwarder_may_see\w*|may_see_intake|_enforce_scope"
    r"|resolve_company_id|get_company_by_code|company_filter_ids|own_company_id|get_vessel_visible)\b")

DICT = "słownik wspólny dla grupy (bez company_id), zapis tylko admin/edytor danych globalnych"
USERS = "konta użytkowników — wyłącznie admin (zarządzanie dostępem, nie dane spółki)"
OWN = "zasób zalogowanego użytkownika (filtr po user.id)"
KNOWLEDGE = "baza wiedzy wspólna dla grupy (bez company_id)"
VESSEL = "statek — dane publiczne AIS wspólne dla wszystkich spółek"

EXCEPTIONS = {
    "DELETE /api/admin/blocked-ips/{blocked_id}": "zablokowane IP — bezpieczeństwo instancji, tylko admin",
    "DELETE /api/auth/sessions/{session_id}": OWN,
    "POST /api/automations/rules/history/{audit_id}/restore": "historia reguł z kreatora — ustawienie globalne, tylko admin",
    "DELETE /api/container-ports/{port_id}": DICT,
    "DELETE /api/customs-agencies/{agency_id}": DICT,
    "DELETE /api/customs/case-statuses/{status_id}": DICT,
    "DELETE /api/customs/doc-templates/{template_id}": DICT,
    "DELETE /api/customs/document-types/{type_id}": DICT,
    "DELETE /api/knowledge/notes/{note_id}": KNOWLEDGE,
    "DELETE /api/material-units/{unit_id}": DICT,
    "DELETE /api/paz/{paz_id}": DICT,
    "DELETE /api/stock-targets/{target_id}": DICT,
    "DELETE /api/users/{user_id}": USERS,
    "DELETE /api/users/{user_id}/sessions/{session_id}": USERS,
    "GET /api/import/sap-imports/{import_id}/errors.xlsx": "import kartoteki SAP — katalog dostawców grupy "
                                                           "(_require_catalog), bez company_id",
    "GET /api/users/{user_id}/avatar": "zdjęcie profilowe — widoczne dla zalogowanych (lista obecności, czat)",
    "GET /api/users/{user_id}/sessions": USERS,
    "PATCH /api/checklist-points/{point_id}": DICT,
    "PATCH /api/companies/{company_id}": "dane spółki — tylko admin",
    "PUT /api/budgets/port/{company_id}": "budżet spółki (US-084) — tylko admin",
    "PATCH /api/customs-agencies/{agency_id}": DICT,
    "PATCH /api/customs/case-statuses/{status_id}": DICT,
    "PATCH /api/customs/doc-templates/{template_id}": DICT,
    "PATCH /api/customs/document-types/{type_id}": DICT,
    "PATCH /api/forwarders/{forwarder_id}": DICT,
    "PATCH /api/knowledge/notes/{note_id}": KNOWLEDGE,
    "PATCH /api/knowledge/topics/{topic_id}/status": KNOWLEDGE,
    "PATCH /api/ports/{port_id}": DICT,
    "PATCH /api/problem-types/{type_id}": DICT,
    "POST /api/knowledge/topics/{topic_id}/vote": KNOWLEDGE,
    "POST /api/tracking/vessels/{vessel_id}/photo": VESSEL,
    "POST /api/tracking/vessels/{vessel_id}/photo/fetch": VESSEL,
    "POST /api/users/{user_id}/2fa/disable": USERS,
    "POST /api/users/{user_id}/reset-invite": USERS,
}


def _guarded(fn, depth: int = 0, seen: set | None = None) -> bool:
    seen = set() if seen is None else seen
    if fn in seen or depth > 2:
        return False
    seen.add(fn)
    try:
        src = inspect.getsource(fn)
    except (OSError, TypeError):
        return False
    if GUARDS.search(src):
        return True
    module = sys.modules.get(fn.__module__)
    for name in set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", src)):
        target = getattr(module, name, None)
        own_code = target.__module__ == fn.__module__ or target.__module__.startswith("app") \
            if inspect.isfunction(target) else False
        if own_code and _guarded(target, depth + 1, seen):
            return True
    return False


def _id_routes():
    return {f"{m} {p}": r for m, p, r in _api_routes()
            if p.startswith("/api") and re.search(r"\{\w*id\}", p)}


def test_routes_with_ids_go_through_isolation_or_are_listed():
    unguarded = sorted(k for k, r in _id_routes().items() if k not in EXCEPTIONS and not _guarded(r.endpoint))
    assert not unguarded, ("Trasy z identyfikatorem bez kontroli spółki (deps.py: get_scoped / scope_* / "
                           "check_container_access) — dodaj kontrolę albo wpis do EXCEPTIONS z powodem:\n  "
                           + "\n  ".join(unguarded))


def test_exceptions_are_current():
    """Wyjątek dla trasy, której już nie ma albo która ma już kontrolę, trzeba usunąć z listy."""
    routes = _id_routes()
    stale = sorted(k for k in EXCEPTIONS if k not in routes or _guarded(routes[k].endpoint))
    assert not stale, "Nieaktualne wyjątki: " + ", ".join(stale)


def test_guard_sees_enough_routes():
    # bezpiecznik: zmiana wewnętrzna FastAPI nie może po cichu wyzerować strażnika
    assert len(_id_routes()) >= 200


def _leaky(container_id, db):
    return db.get("Container", container_id)          # bez kontroli spółki


def _helper(db, container_id, user):
    return get_container_checked(db, container_id, user)   # noqa: F821 — tylko źródło dla strażnika


def _safe(container_id, db, user):
    return _helper(db, container_id, user)


def test_guard_detects_missing_check_and_follows_helpers():
    assert not _guarded(_leaky)
    assert _guarded(_safe)   # kontrola w funkcji pomocniczej tego samego modułu
