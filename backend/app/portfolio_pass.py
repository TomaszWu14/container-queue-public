"""Przepustka z portfolio: ciasteczko `gosc` (HttpOnly, domena .twapp.pl) wpuszcza na demo bez formularza.

Frontend nie widzi ciasteczka HttpOnly, więc sprawdza je backend: przy wejściu na konto demo
pytamy portfolio (`GET {PORTFOLIO_URL}/api/gosc`, tylko nagłówek `Cookie: gosc=...`, 2 s, bez
przekierowań). Wynik wyłącznie po kodzie statusu (200 = ok). Każdy błąd = brak przepustki
(zachowanie jak dotąd: formularz „przedstaw się”), nigdy 500. Wartości ciasteczka nie logujemy;
w cache trzymamy tylko jej hash, pozytywny wynik na 10 minut.
"""
import hashlib
import logging
import threading
import time

import httpx

from .config import settings

logger = logging.getLogger(__name__)

COOKIE = "gosc"
MAX_COOKIE_LEN = 200
TIMEOUT_S = 2.0
CACHE_TTL_S = 600
CACHE_MAX = 1000

_cache: dict[str, float] = {}   # sha256(token) -> wygaśnięcie (monotonic)
_lock = threading.Lock()
_warned = False


def _base_url() -> str | None:
    """PORTFOLIO_URL tylko z https://; inaczej sprawdzanie wyłączone (ostrzeżenie w logu)."""
    global _warned
    url = settings.portfolio_url.strip().rstrip("/")
    if url.startswith("https://"):
        return url
    if not _warned:
        _warned = True
        logger.warning("PORTFOLIO_URL nie zaczyna się od https:// — przepustka z portfolio wyłączona")
    return None


def has_pass(token: str | None) -> bool:
    """True, gdy portfolio potwierdza ciasteczko `gosc` (200). Bez ciasteczka — bez ruchu sieciowego."""
    if not settings.portfolio_pass or not token or len(token) > MAX_COOKIE_LEN:
        return False
    base = _base_url()
    if base is None:
        return False
    key = hashlib.sha256(token.encode("utf-8")).hexdigest()
    now = time.monotonic()
    with _lock:
        if _cache.get(key, 0.0) > now:
            return True
    try:
        resp = httpx.get(f"{base}/api/gosc", headers={"Cookie": f"{COOKIE}={token}"},
                         timeout=TIMEOUT_S, follow_redirects=False)
    except Exception as exc:  # noqa: BLE001 — błąd sieci = brak przepustki, nie 500
        logger.warning("Sprawdzenie przepustki portfolio nie powiodło się: %s", type(exc).__name__)
        return False
    if resp.status_code != 200:
        return False
    with _lock:
        if len(_cache) >= CACHE_MAX:
            _cache.clear()
        _cache[key] = now + CACHE_TTL_S
    return True


def clear_cache() -> None:
    with _lock:
        _cache.clear()
