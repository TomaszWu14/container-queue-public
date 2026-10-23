"""Powiadomienie push (ntfy) o nowym gościu bramki demo.

Po udanym zapisie w bramce „przedstaw się” właściciel dostaje push na telefon (aplikacja ntfy).
Wysyłka w wątku daemon — gość nie czeka na ntfy; każdy błąd to tylko ostrzeżenie w logu.
Bez `NTFY_URL` funkcja nic nie robi (zero ruchu sieciowego, także w testach).
"""
import logging
import threading

import httpx

from .config import settings

logger = logging.getLogger(__name__)

APP = "container-queue"
TIMEOUT_S = 5
MAX_BODY = 300


def _send(url: str, body: str, token: str) -> None:
    headers = {"Title": f"Nowy gosc: {APP}", "Tags": "bell", "Priority": "high",
               "Content-Type": "text/plain; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        httpx.post(url, content=body.encode("utf-8"), headers=headers,
                   timeout=TIMEOUT_S).raise_for_status()
    except Exception as exc:  # noqa: BLE001 — powiadomienie nie może zaszkodzić gościowi
        logger.warning("Powiadomienie ntfy o gościu demo nie wysłane: %s", type(exc).__name__)


def _start(target, *args) -> None:
    threading.Thread(target=target, args=args, daemon=True, name="ntfy-visitor").start()


def notify_visitor(first_name: str, last_name: str, company: str) -> None:
    """Wysyła w tle push „{imię} {nazwisko} ({firma}) wszedł do {APP}”; bez NTFY_URL = no-op."""
    url = settings.ntfy_url.strip()
    if not url:
        return
    if not url.lower().startswith(("https://", "http://")):
        logger.warning("NTFY_URL musi zaczynać się od https:// lub http:// — powiadomienie pominięte")
        return
    body = f"{first_name} {last_name} ({company}) wszedł do {APP}"[:MAX_BODY]
    try:
        _start(_send, url, body, settings.ntfy_token.strip())
    except Exception as exc:  # noqa: BLE001 — np. brak wątków; gość i tak wchodzi
        logger.warning("Nie udało się uruchomić powiadomienia ntfy: %s", type(exc).__name__)
