"""Walidacja konfiguracji przy starcie (fail-fast produkcji).

Wydzielone z app/main.py (limit 500 linii, US-001); main re-eksportuje te nazwy. Logger zostaje
„app.main”, żeby komunikaty startu w logach i testach miały tę samą nazwę co dotąd."""
import logging

from .config import settings
from .rate_limit import assert_worker_config

logger = logging.getLogger("app.main")

# to NIE są sekrety, tylko lista niebezpiecznych wartości domyślnych, którą wykrywamy
INSECURE_DEFAULTS = {"secret_key": "change-me-in-production",  # nosec B105
                     "admin_password": "admin123"}  # nosec B105


def _warn_ollama_url() -> None:
    """AI-006: Ollama bez uwierzytelniania — odrzucony adres = AI wyłączone + ostrzeżenie."""
    from urllib.parse import urlsplit

    from .llm import is_internal_host, url_problem
    url = settings.ollama_url.strip()
    if not url:
        return
    problem = url_problem(url)
    parts = urlsplit(url)
    if problem:
        logger.warning("OLLAMA_URL odrzucony (%s) — funkcje AI wyłączone.", problem)
    elif parts.scheme == "http" and not is_internal_host(parts.hostname or ""):
        logger.warning("OLLAMA_URL po HTTP z OLLAMA_ALLOW_REMOTE=true — skany faktur "
                       "idą bez szyfrowania; użyj https albo sieci Dockera.")


def _is_postgres_url(url: str) -> bool:
    from sqlalchemy.engine import make_url
    from sqlalchemy.exc import ArgumentError
    try:
        return make_url(url).get_backend_name() == "postgresql"
    except (ArgumentError, ValueError):   # ValueError: zły port — odmowa, nie traceback
        return False


def validate_settings() -> None:
    """Fail fast: produkcja nie może wystartować z domyślnymi sekretami ani bez
    bezpiecznych cookies (uwierzytelnianie po HTTP = przejęcie sesji)."""
    assert_worker_config()   # BUILD-003: >1 worker tylko na PG; każde środowisko
    is_prod = settings.environment.lower() in ("production", "prod")
    insecure = [name for name, default in INSECURE_DEFAULTS.items()
                if getattr(settings, name) == default]
    if is_prod and not settings.secure_cookies:
        if settings.allow_insecure_http:
            logger.warning("ALLOW_INSECURE_HTTP=true — produkcja po HTTP, sesje do przejęcia w sieci; "
                           "włącz HTTPS i SECURE_COOKIES=true.")
        else:
            insecure.append("secure_cookies")
    if is_prod and not _is_postgres_url(settings.database_url):
        # US-001 (R-04): bez DATABASE_URL domyślny SQLite = pusta baza w kontenerze, bez kopii
        insecure.append("database_url (wymagany PostgreSQL)")
    if is_prod and settings.bcrypt_rounds < 12:
        # niższy koszt = hashe haseł łamalne offline szybciej; 4 jest tylko dla testów
        insecure.append("bcrypt_rounds (min. 12)")
    if is_prod and len(settings.secret_key) < 32:
        # słaby (choć niedomyślny) sekret HS256 jest łamalny offline → wymuszamy min. 32 znaki
        insecure.append("secret_key (min. 32 znaki)")
    if is_prod and not settings.public_base_url:
        # bez tego linki e-mail (reset hasła) budują się z nagłówka Host = host-header injection
        insecure.append("public_base_url")
    if is_prod and settings.automation_api_token and len(settings.automation_api_token) < 32:
        # token serwisowy n8n jest sekretem długoterminowym bez wygaśnięcia — krótki
        # da się zgadnąć, a otwiera API z uprawnieniami konta serwisowego
        insecure.append("automation_api_token (min. 32 znaki)")
    _warn_ollama_url()
    if settings.automation_webhook_url and not settings.automation_webhook_secret:
        logger.warning("AUTOMATION_WEBHOOK_URL bez AUTOMATION_WEBHOOK_SECRET — zdarzenia "
                       "lecą bez podpisu HMAC; zabezpiecz webhook n8n inaczej (header auth).")
    if not insecure:
        return
    message = ("Konfiguracja wymaga zmiany dla produkcji: "
               + ", ".join(f"{n.upper()}" for n in insecure))
    if is_prod:
        raise RuntimeError(message)
    logger.warning("%s (dozwolone tylko poza produkcją, ENVIRONMENT=%s)",
                   message, settings.environment)
