"""Powiadomienia push (ntfy) o gościach bramki demo.

Po udanym zapisie w bramce „przedstaw się” właściciel dostaje push na telefon (aplikacja ntfy);
drugi, jednorazowy push przychodzi, gdy gość obejrzy `NTFY_ENGAGED_VIEWS` ekranów. Firma z listy
`NTFY_WATCH_COMPANIES` (frazy po przecinku, tylko w env) podnosi push do `Priority: urgent`.
Wysyłka w wątku daemon — gość nie czeka na ntfy; każdy błąd to tylko ostrzeżenie w logu.
Bez `NTFY_URL` funkcje nic nie robią (zero ruchu sieciowego, także w testach).
"""
import logging
import threading
import unicodedata

import httpx

from .config import settings

logger = logging.getLogger(__name__)

APP = "container-queue"
TIMEOUT_S = 5
MAX_BODY = 300
MIN_PHRASE = 2


def normalize(text: str) -> str:
    """casefold + bez polskich/obcych znaków diakrytycznych (NFKD) + pojedyncze spacje."""
    decomposed = unicodedata.normalize("NFKD", (text or "").casefold().replace("ł", "l"))
    return " ".join("".join(c for c in decomposed if not unicodedata.combining(c)).split())


def is_watched(company: str) -> bool:
    """Czy firma gościa zawiera którąś frazę z NTFY_WATCH_COMPANIES (po normalizacji)."""
    name = normalize(company)
    phrases = (normalize(p) for p in settings.ntfy_watch_companies.split(","))
    return any(len(p) >= MIN_PHRASE and p in name for p in phrases)


def _send(url: str, body: str, token: str, headers: dict[str, str]) -> None:
    headers = {**headers, "Content-Type": "text/plain; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        httpx.post(url, content=body.encode("utf-8"), headers=headers,
                   timeout=TIMEOUT_S).raise_for_status()
    except Exception as exc:  # noqa: BLE001 — powiadomienie nie może zaszkodzić gościowi
        logger.warning("Powiadomienie ntfy o gościu demo nie wysłane: %s", type(exc).__name__)


def _start(target, *args) -> None:
    threading.Thread(target=target, args=args, daemon=True, name="ntfy-visitor").start()


def _push(body: str, headers: dict[str, str]) -> None:
    url = settings.ntfy_url.strip()
    if not url:
        return
    if not url.lower().startswith(("https://", "http://")):
        logger.warning("NTFY_URL musi zaczynać się od https:// lub http:// — powiadomienie pominięte")
        return
    try:
        _start(_send, url, body[:MAX_BODY], settings.ntfy_token.strip(), headers)
    except Exception as exc:  # noqa: BLE001 — np. brak wątków; gość i tak wchodzi
        logger.warning("Nie udało się uruchomić powiadomienia ntfy: %s", type(exc).__name__)


def notify_visitor(first_name: str, last_name: str, company: str) -> None:
    """Push „{imię} {nazwisko} ({firma}) wszedł do {APP}”; firma z listy → alarm urgent."""
    body = f"{first_name} {last_name} ({company}) wszedł do {APP}"
    if is_watched(company):
        _push("⚠️ " + body, {"Title": f"UWAGA firma z listy: {APP}", "Tags": "rotating_light",
                             "Priority": "urgent"})
    else:
        _push(body, {"Title": f"Nowy gosc: {APP}", "Tags": "bell", "Priority": "high"})


def notify_engaged(first_name: str, last_name: str, company: str, views: int) -> None:
    """Jednorazowy push „gość ogląda demo” po `views` ekranach; firma z listy → urgent."""
    body = f"{first_name} {last_name} ({company}) obejrzał już {views} ekranów w {APP}"
    _push(body, {"Title": f"Gosc oglada demo: {APP}", "Tags": "eyes",
                 "Priority": "urgent" if is_watched(company) else "default"})
